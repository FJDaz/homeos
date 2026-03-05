import requests
import concurrent.futures

# Names found in search results
author_slugs = [
    "madin", "winterzone", "floria", "whakaaro", "madoo", "madoe", "snowy", "honebee", 
    "heartstar", "barley", "baowe", "chupacabra", "gadden", "luxdiamond", "sasspark", 
    "empathy", "giftxtore", "mellow", "yorn", "rinbuild", "muzilla", "mistri", 
    "ryenking", "honshi", "wanzor", "graingrower", "evergreen", "boston", "biwors", 
    "roonix", "snowy", "honeybee", "heartstar", "barley", "baowe", "heart-star",
    "winter-zone", "honeybee", "heart-star", "sass-park", "gift-xtore", "floria",
    "snowy-wp", "baowe-wp", "madoo-wp", "madoe-wp"
]

prefixes = ["", "ms-", "madsparrow-", "wp-", "demo-"]

all_to_test = []
for name in author_slugs:
    for pref in prefixes:
        all_to_test.append(pref + name)

# Remove duplicates
all_to_test = list(set(all_to_test))

def check_theme(theme):
    url = f"https://theme.madsparrow.me/{theme}/?storefront=envato-elements"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            low_content = response.text.lower()
            if "404" not in low_content[:1000] and "not found" not in low_content[:1000]:
                if "wp-content" in low_content:
                    return theme, url
    except:
        pass
    return None

def main():
    print(f"Testing {len(all_to_test)} variations...")
    working_themes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_theme, all_to_test)
        for res in results:
            if res:
                working_themes.append(res)
                print(f"✅ FOUND: {res[0]}")
    
    print(f"\nTotal working themes found: {len(working_themes)}")
    working_themes.sort()
    for i, (theme, url) in enumerate(working_themes, 1):
        print(f"{i}. {theme}: {url}")

if __name__ == "__main__":
    main()
