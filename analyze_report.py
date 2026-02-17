import json

try:
    with open('lighthouse-report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    audits = data.get('audits', {})

    print("--- Opportunities (Score < 1) ---")
    for key, audit in audits.items():
        if audit.get('details', {}).get('type') == 'opportunity' and audit.get('score', 1) < 1:
            print(f"ID: {key}")
            print(f"Title: {audit.get('title')}")
            print(f"Score: {audit.get('score')}")
            print(f"Savings (FCP): {audit.get('metricSavings', {}).get('FCP')}")
            print(f"Savings (LCP): {audit.get('metricSavings', {}).get('LCP')}")
            # Print items if available
            if 'details' in audit and 'items' in audit['details']:
                for item in audit['details']['items']:
                     print(f" - {item.get('url', 'No URL')}: {item.get('totalBytes', 0)} bytes, {item.get('wastedMs', 0)} ms")
            print("-" * 20)

except Exception as e:
    print(f"Error parsing report: {e}")
