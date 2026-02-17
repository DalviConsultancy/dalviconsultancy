import json

try:
    with open('lighthouse-report-v3.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    audits = data.get('audits', {})
    categories = data.get('categories', {})

    fcp = audits.get('first-contentful-paint', {}).get('displayValue')
    lcp = audits.get('largest-contentful-paint', {}).get('displayValue')
    tbt = audits.get('total-blocking-time', {}).get('displayValue')
    cls = audits.get('cumulative-layout-shift', {}).get('displayValue')
    
    perf = categories.get('performance', {}).get('score')
    
    # Check server response time
    ttfb = audits.get('server-response-time', {}).get('displayValue')

    print(f"Performance: {int(perf * 100)}")
    print(f"FCP: {fcp}")
    print(f"LCP: {lcp}")
    print(f"TBT: {tbt}")
    print(f"CLS: {cls}")
    print(f"TTFB: {ttfb}")

except Exception as e:
    print(f"Error: {e}")
