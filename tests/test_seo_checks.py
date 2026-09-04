from backend.tools.seo_checks import SEOChecker

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SEO Optimization Guide - Master On-Page SEO Best Practices</title>
    <meta name="description" content="Discover everything about SEO optimization guide. Read our comprehensive 2026 expert guide to get actionable insights, proven tips, and best results. Learn more today!">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="canonical" href="https://example.com/seo-guide" />
</head>
<body>
    <h1>SEO Optimization Guide for Beginners</h1>
    <h2>What is SEO Optimization?</h2>
    <p>SEO optimization guide helps search engines understand your website content. By improving title tags, meta descriptions, readability, and speed, you can rank higher in Google search results.</p>
    <img src="seo-chart.jpg" alt="SEO optimization chart" loading="lazy" />
    <a href="/blog/internal-link">Internal Link</a>
    <a href="https://external-authority.com" rel="nofollow">Authority Source</a>
</body>
</html>
"""

def test_seo_checks_pass():
    checker = SEOChecker(SAMPLE_HTML, "https://example.com/seo-guide", keyword="seo optimization guide")
    checks = checker.run_all_checks()
    
    assert len(checks) >= 8
    title_chk = next(c for c in checks if c["id"] == "title_tag")
    assert title_chk["status"] == "pass"
    assert title_chk["score"] == 100

    meta_chk = next(c for c in checks if c["id"] == "meta_description")
    assert meta_chk["status"] == "pass"
