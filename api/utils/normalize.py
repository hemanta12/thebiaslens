from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import re


def canonicalize_url(url: str) -> str:
    # Parse the URL
    parsed = urlparse(url)
    
    # Normalize scheme to https if http
    scheme = 'https' if parsed.scheme in ['http', 'https'] else parsed.scheme
    
    # Normalize hostname to lowercase
    netloc = parsed.netloc.lower()
    
    # Remove common tracking parameters
    tracking_params = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'utm_id', 'utm_campaign_id', 'utm_adgroup_id', 'utm_keyword',
        'gclid', 'fbclid', 'msclkid', 'twclid', 'li_fat_id',
        '_ga', '_gl', '_hsenc', '_hsmi', 'mc_cid', 'mc_eid',
        'ref', 'source', 'campaign', 'medium'
    }
    
    # Parse query parameters and filter out tracking ones
    query_params = parse_qs(parsed.query, keep_blank_values=False)
    filtered_params = {
        k: v for k, v in query_params.items() 
        if k.lower() not in tracking_params
    }
    
    # Rebuild query string
    new_query = urlencode(filtered_params, doseq=True) if filtered_params else ''
    
    # Reconstruct URL
    canonical = urlunparse((
        scheme,
        netloc,
        parsed.path,
        parsed.params,
        new_query,
        ''  # Remove fragment
    ))
    
    return canonical


def infer_source_from_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc.lower()
        
        # Remove www. prefix
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        
        # Handle common news domains
        domain_map = {
            'cnn.com': 'CNN',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'reuters.com': 'Reuters',
            'ap.org': 'Associated Press',
            'bloomberg.com': 'Bloomberg',
            'wsj.com': 'The Wall Street Journal',
            'theguardian.com': 'The Guardian',
            'foxnews.com': 'Fox News',
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'cbsnews.com': 'CBS News',
            'usatoday.com': 'USA Today',
            'politico.com': 'Politico',
            'npr.org': 'NPR',
            'time.com': 'Time',
            'newsweek.com': 'Newsweek'
        }
        
        if hostname in domain_map:
            return domain_map[hostname]
        
        # For unknown domains, capitalize first letter and remove .com/.org etc
        domain_parts = hostname.split('.')
        if len(domain_parts) >= 2:
            # Take the second-to-last part (e.g., 'example' from 'www.example.com')
            base_name = domain_parts[-2]
            return base_name.capitalize()
        
        return hostname.capitalize()
        
    except Exception:
        # Fallback to the original URL if parsing fails
        return url