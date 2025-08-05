import requests


def get_newsletter_data(base_url, lang):
    url = f"{base_url}/api/newsletter/telegram?locale={lang}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data["newsletter"] is not None:
            return data["message"]
        else:
            return "Viikkotiedote on tyhjä" if lang == "fi" else "Weekly news is empty"
    elif response.status_code == 404:
        return (
            "Viikkotiedotetta ei löytynyt" if lang == "fi" else "Weekly news not found"
        )
    else:
        return (
            "Virhe viikkotiedotetta haettaessa"
            if lang == "fi"
            else "Error fetching weekly news"
        )
