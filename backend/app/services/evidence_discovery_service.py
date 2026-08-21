import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

try:
    try:
        from ddgs import DDGS
        HAS_DDGS = True
    except ImportError:
        from duckduckgo_search import DDGS
        HAS_DDGS = True
except ImportError:
    HAS_DDGS = False


class EvidenceDiscoveryService:
    """
    Evidence-Discovery & CRAG (Corrective RAG) Semantic Engine.
    Web search is NOT the knowledge base; it is an evidence-discovery mechanism
    for products the local DuckDB knowledge base cannot confidently resolve.
    """

    BANNED_MARKETPLACES = [
        "amazon.com", "amazon.in", "ebay.com", "aliexpress.com", "alibaba.com",
        "walmart.com", "temu.com", "wish.com", "rakuten.com", "flipkart.com"
    ]

    @classmethod
    def is_banned_marketplace(cls, url: str) -> bool:
        """Check if URL belongs to a low-authority or banned consumer marketplace."""
        if not url:
            return False
        u_lower = url.lower()
        return any(banned in u_lower for banned in cls.BANNED_MARKETPLACES)

    @classmethod
    def evaluate_source_quality(cls, url: str, title: str = "") -> float:
        """
        CRAG Source Quality Scorer:
        1.00 = Official OEM Product Page
        0.92 = Authoritative Technical Datasheet / Specification Sheet PDF
        0.75 = Authorized Industrial Distributor / Technical Resource
        0.00 = Banned Marketplace (Amazon, eBay, etc.)
        """
        if not url or cls.is_banned_marketplace(url):
            return 0.0
        
        u_lower = url.lower()
        t_lower = title.lower()

        if u_lower.endswith(".pdf") or "datasheet" in u_lower or "spec-sheet" in u_lower or "manual" in u_lower:
            return 0.92
        if "manufacturer" in t_lower or "official" in t_lower or "oem" in t_lower:
            return 0.95
        if any(auth in u_lower for auth in ["supply", "industrial", "electric", "automation"]):
            return 0.75
        return 0.80

    @classmethod
    def sanitize_search_token(cls, text: str) -> str:
        """Strip dangerous search engine punctuation (quotes, hyphens, colons, wildcards)."""
        if not text:
            return ""
        # Remove quotes, dashes, colons, slashes
        clean = re.sub(r'["\'\-:;/\\]', ' ', str(text))
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @classmethod
    def discover_web_evidence(
        cls,
        mpn: str,
        brand: str = "",
        desc: str = "",
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Targeted Evidence Discovery via DuckDuckGo with Sanitized Multi-Tier Queries.
        """
        clean_mpn = cls.sanitize_search_token(mpn)
        clean_brand = cls.sanitize_search_token(brand.replace("®", "").replace("™", ""))
        clean_desc = cls.sanitize_search_token(desc)

        if not clean_mpn and not clean_desc:
            return []

        # Construct hierarchical search queries
        queries_to_try = []
        if clean_brand and clean_mpn and clean_brand.lower() not in ["unbranded", "no unilog brand"]:
            queries_to_try.append(f"{clean_brand} {clean_mpn} specifications")
            queries_to_try.append(f"{clean_brand} {clean_mpn} datasheet")
        elif clean_mpn:
            queries_to_try.append(f"{clean_mpn} specifications")
            queries_to_try.append(f"{clean_mpn} datasheet")
        
        if clean_desc:
            # Take first 5 words of description
            desc_words = " ".join(clean_desc.split()[:6])
            queries_to_try.append(f"{clean_brand} {desc_words}")

        evidence_items: List[Dict[str, Any]] = []

        for q in queries_to_try:
            if evidence_items:
                break
            try:
                with DDGS(timeout=5) as ddgs:
                    results = list(ddgs.text(q, max_results=max_results))
                    for r in results:
                        url = r.get("href") or r.get("link") or ""
                        title = r.get("title") or ""
                        snippet = r.get("body") or r.get("snippet") or ""

                        # Filter against banned marketplaces
                        if cls.is_banned_marketplace(url):
                            continue

                        quality_score = cls.evaluate_source_quality(url, title)
                        if quality_score > 0.0:
                            evidence_items.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "source_quality": quality_score,
                                "is_pdf": url.lower().endswith(".pdf")
                            })
                if evidence_items:
                    logger.info(f"    • Discovered {len(evidence_items)} authoritative web evidence sources for '{q}'")
            except Exception as e:
                logger.debug(f"[EvidenceDiscoveryService] Search query '{q}' fallback: {e}")

        return evidence_items

    @classmethod
    def rank_best_evidence(
        cls,
        query: str,
        evidence_items: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Semantic + Spec-Density Reranker:
        Combines TF-IDF cosine similarity with technical spec density
        (presence of dimensions, numerical ratings, units) to select top authoritative snippets.
        """
        if not evidence_items:
            return []

        snippets = [f"{e.get('title', '')} {e.get('snippet', '')}" for e in evidence_items]
        
        # 1. Semantic TF-IDF Cosine Similarity
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform([query] + snippets)
            cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        except Exception:
            cosine_sims = np.zeros(len(evidence_items))

        # 2. Spec Density Scoring
        spec_regex = re.compile(r"\b(\d+(\.\d+)?|\d+/\d+)\s*(in|mm|v|a|w|psi|rpm|gpm|hp|kaic|awg|dba|oz|ml)\b", re.IGNORECASE)

        ranked = []
        for idx, item in enumerate(evidence_items):
            semantic_score = float(cosine_sims[idx]) if idx < len(cosine_sims) else 0.5
            snippet_text = snippets[idx]
            spec_matches = len(spec_regex.findall(snippet_text))
            spec_density_score = min(1.0, spec_matches * 0.2)
            source_quality = item.get("source_quality", 0.7)

            # Combined Reranked Score
            combined_score = round((source_quality * 0.45) + (semantic_score * 0.35) + (spec_density_score * 0.20), 3)
            item["rerank_score"] = combined_score
            ranked.append(item)

        ranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return ranked[:top_k]

    @classmethod
    def discover_product_images(
        cls,
        mpn: str,
        brand: str = "",
        desc: str = "",
        max_images: int = 5
    ) -> List[str]:
        """
        Discover real product image URLs via DuckDuckGo Image Search.
        Returns a list of direct image URLs (jpg/png/webp) from authoritative non-marketplace sources.
        Filtered against banned marketplaces and sorted by source quality.
        """
        if not HAS_DDGS:
            return []

        clean_mpn = cls.sanitize_search_token(mpn)
        clean_brand = cls.sanitize_search_token(brand.replace("®", "").replace("™", ""))

        if not clean_mpn:
            return []

        queries = []
        if clean_brand and clean_brand.lower() not in ["unbranded", "no unilog brand", ""]:
            queries.append(f"{clean_brand} {clean_mpn} product")
            queries.append(f"{clean_brand} {clean_mpn}")
        else:
            queries.append(f"{clean_mpn} product")

        collected: List[str] = []

        for q in queries:
            if len(collected) >= max_images:
                break
            try:
                with DDGS(timeout=8) as ddgs:
                    results = list(ddgs.images(q, max_results=max_images * 3))
                    for r in results:
                        img_url = r.get("image") or r.get("url") or ""
                        src_url = r.get("url") or r.get("source") or ""

                        if not img_url:
                            continue
                        # Skip banned marketplace sources
                        if cls.is_banned_marketplace(src_url) or cls.is_banned_marketplace(img_url):
                            continue
                        # Only accept direct image file URLs
                        img_lower = img_url.lower()
                        if not any(img_lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                            # Try to still include if it has image-like path
                            if not any(x in img_lower for x in ["/images/", "/img/", "/product/", "/media/"]):
                                continue

                        if img_url not in collected:
                            collected.append(img_url)
                        if len(collected) >= max_images:
                            break

                if collected:
                    logger.info(f"    [ImageSearch] Found {len(collected)} real product images for '{q}'")
                    break
            except Exception as e:
                logger.debug(f"[EvidenceDiscoveryService] Image search '{q}' fallback: {e}")

        return collected[:max_images]
