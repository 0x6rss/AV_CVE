import subprocess
import sys
import os
import requests
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
import threading
from tzlocal import get_localzone
from googletrans import Translator


def is_package_installed(package):
    try:
        subprocess.check_output([sys.executable, '-m', 'pip', 'show', package])
        return True
    except subprocess.CalledProcessError:
        return False

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def setup():
    packages = [
        "requests",
        "rich",
        "tzlocal",
        "googletrans==4.0.0-rc1"
    ]
    
    for package in packages:
        if not is_package_installed(package):
            print(f"{package} yükleniyor...")
            install_package(package)
        else:
            print(f"{package} zaten yüklü.")

    if os.name == 'nt':
        subprocess.call('cls', shell=True)
    else:
        subprocess.call('clear', shell=True)

SETTINGS_FILE = 'settings.json'
LAST_SEARCH_FILE = 'last_search.json'
console = Console()
translator = Translator()


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as file:
        json.dump(settings, file)


def get_github_token():
    settings = load_settings()
    if 'GITHUB_TOKEN' in settings:
        return settings['GITHUB_TOKEN']
    token = Prompt.ask("[bold yellow]GitHub tokeninizi girin[/bold yellow]")
    settings['GITHUB_TOKEN'] = token
    save_settings(settings)
    return token


def load_last_search_time():
    if os.path.exists(LAST_SEARCH_FILE):
        with open(LAST_SEARCH_FILE, 'r') as file:
            data = json.load(file)
            return datetime.fromisoformat(data['last_search_time'])
    return None


def save_last_search_time(time):
    with open(LAST_SEARCH_FILE, 'w') as file:
        json.dump({'last_search_time': time.isoformat()}, file)


def handle_existing_last_search_file():
    if os.path.exists(LAST_SEARCH_FILE):
        console.print("[bold yellow]Son arama dosyası zaten mevcut. Bu yeni CVE'leri bulmayı engelleyebilir.[/bold yellow]")
        action = Prompt.ask("[bold cyan]Son arama dosyasını silmek veya yeniden adlandırmak ister misiniz? (sil/yeni ad/veri)[/bold cyan]", default="veri")
        if action == "sil":
            os.remove(LAST_SEARCH_FILE)
            console.print("[bold green]Son arama dosyası silindi.[/bold green]")
        elif action == "yeni ad":
            new_name = Prompt.ask("[bold cyan]Son arama dosyası için yeni ad girin[/bold cyan]")
            os.rename(LAST_SEARCH_FILE, new_name)
            console.print(f"[bold green]Son arama dosyası {new_name} olarak yeniden adlandırıldı.[/bold green]")
        else:
            console.print("[bold yellow]Mevcut son arama dosyası ile devam ediliyor.[/bold yellow]")


def clone_repository(repo_url, repo_name):
    try:
        subprocess.run(["git", "clone", repo_url, repo_name], check=True)
        console.print(f"[bold green]Başarıyla klonlandı {repo_name}[/bold green]")
    except subprocess.CalledProcessError:
        console.print(f"[bold red]{repo_name} klonlanamadı[/bold red]")

def fetch_repositories(url, headers, repos):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            results = response.json()
            for repo in results['items']:
                repos.append(repo)
        else:
            console.print(f"[bold red]GitHub API'den veri alınamadı. Durum kodu: {response.status_code}[/bold red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Bir hata oluştu: {str(e)}[/bold red]")


def translate_description(description):
    if description:
        try:
            translated = translator.translate(description, src='en', dest='tr')
            return translated.text
        except Exception as e:
            console.print(f"[bold red]Çeviri hatası: {str(e)}[/bold red]")
            return description
    return '[bold red]Açıklama yok[/bold red]'


def search_new_cves():
    github_token = get_github_token()
    timezone = str(get_localzone())
    headers = {'Authorization': f'token {github_token}'}
    
    last_search_time = load_last_search_time() or datetime.now() - timedelta(days=1)
    query = f'CVE created:>{last_search_time.strftime("%Y-%m-%dT%H:%M:%SZ")} in:readme,description'
    url = f'https://api.github.com/search/repositories?q={query}&per_page=10'

    repos = []
    threads = []
    for page in range(1, 6):  # Fetching up to 50 repositories (5 pages, 10 per page)
        paginated_url = f'{url}&page={page}'
        thread = threading.Thread(target=fetch_repositories, args=(paginated_url, headers, repos))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    if repos:
        table = Table(title="[bold magenta]Yeni CVE'ler Bulundu[/bold magenta]", show_header=True, header_style="bold blue")
        table.add_column("No.", style="bold red", width=5)
        table.add_column("Ad", style="bold green", no_wrap=True)
        table.add_column("URL", style="bold cyan")
        table.add_column("Açıklama", style="bold yellow")
        table.add_column("Oluşturulma Tarihi", style="bold magenta", no_wrap=True)

        for idx, repo in enumerate(repos, start=1):
            description = translate_description(repo['description'])
            table.add_row(str(idx), repo['name'], repo['html_url'], description, repo['created_at'])
            table.add_row("-" * 5, "-" * 30, "-" * 30, "-" * 30, "-" * 20)

        console.print(table)

        while True:
            repo_index = Prompt.ask("[bold yellow]Klonlamak istediğiniz depo numarasını girin (veya 'çıkış' ile çıkın)[/bold yellow]", default="çıkış")
            if repo_index.lower() == 'çıkış':
                break
            try:
                repo_index = int(repo_index) - 1
                if 0 <= repo_index < len(repos):
                    repo = repos[repo_index]
                    clone_repository(repo['html_url'], repo['name'])
                else:
                    console.print("[bold red]Geçersiz numara. Lütfen tekrar deneyin.[/bold red]")
            except ValueError:
                console.print("[bold red]Geçersiz giriş. Lütfen bir numara veya 'çıkış' girin.[/bold red]")
    else:
        console.print("[bold red]Yeni CVE bulunamadı.[/bold red]")

    save_last_search_time(datetime.now())


def search_specific_cve_or_keyword(search_term):
    github_token = get_github_token()
    headers = {'Authorization': f'token {github_token}'}
    query = f'{search_term} in:readme,description'
    url = f'https://api.github.com/search/repositories?q={query}'

    repos = []
    fetch_repositories(url, headers, repos)

    if repos:
        table = Table(title=f"[bold magenta]{search_term} için Depolar[/bold magenta]", show_header=True, header_style="bold blue")
        table.add_column("No.", style="bold red", width=5)
        table.add_column("Ad", style="bold green", no_wrap=True)
        table.add_column("URL", style="bold cyan")
        table.add_column("Açıklama", style="bold yellow")
        table.add_column("Oluşturulma Tarihi", style="bold magenta", no_wrap=True)

        for idx, repo in enumerate(repos, start=1):
            description = translate_description(repo['description'])
            table.add_row(str(idx), repo['name'], repo['html_url'], description, repo['created_at'])
            table.add_row("-" * 5, "-" * 30, "-" * 30, "-" * 30, "-" * 20)

        console.print(table)

        while True:
            repo_index = Prompt.ask("[bold yellow]Klonlamak istediğiniz depo numarasını girin (veya 'çıkış' ile çıkın)[/bold yellow]", default="çıkış")
            if repo_index.lower() == 'çıkış':
                break
            try:
                repo_index = int(repo_index) - 1
                if 0 <= repo_index < len(repos):
                    repo = repos[repo_index]
                    clone_repository(repo['html_url'], repo['name'])
                else:
                    console.print("[bold red]Geçersiz numara. Lütfen tekrar deneyin.[/bold red]")
            except ValueError:
                console.print("[bold red]Geçersiz giriş. Lütfen bir numara veya 'çıkış' girin.[/bold red]")
    else:
        console.print(f"[bold red]{search_term} için depo bulunamadı.[/bold red]")


def search_cves_by_date():
    while True:
        try:
            search_date_str = Prompt.ask("[bold yellow]Arama tarihi girin (YYYY-MM-DD) veya 'çıkış' ile iptal edin[/bold yellow]", default="çıkış")
            if search_date_str.lower() == 'çıkış':
                return
            search_date = datetime.strptime(search_date_str, "%Y-%m-%d")
            break
        except ValueError:
            console.print("[bold red]Geçersiz tarih formatı. Lütfen tarihi YYYY-MM-DD formatında girin.[/bold red]")

    github_token = get_github_token()
    timezone = str(get_localzone())
    headers = {'Authorization': f'token {github_token}'}
    
    query = f'CVE created:{search_date.strftime("%Y-%m-%d")} in:readme,description'
    url = f'https://api.github.com/search/repositories?q={query}&per_page=10'

    repos = []
    fetch_repositories(url, headers, repos)

    if repos:
        table = Table(title=f"[bold magenta]{search_date.strftime('%Y-%m-%d')} tarihinde oluşturulan CVE'ler[/bold magenta]", show_header=True, header_style="bold blue")
        table.add_column("No.", style="bold red", width=5)
        table.add_column("Ad", style="bold green", no_wrap=True)
        table.add_column("URL", style="bold cyan")
        table.add_column("Açıklama", style="bold yellow")
        table.add_column("Oluşturulma Tarihi", style="bold magenta", no_wrap=True)

        for idx, repo in enumerate(repos, start=1):
            description = translate_description(repo['description'])
            table.add_row(str(idx), repo['name'], repo['html_url'], description, repo['created_at'])
            table.add_row("-" * 5, "-" * 30, "-" * 30, "-" * 30, "-" * 20)

        console.print(table)

        while True:
            repo_index = Prompt.ask("[bold yellow]Klonlamak istediğiniz depo numarasını girin (veya 'çıkış' ile çıkın)[/bold yellow]", default="çıkış")
            if repo_index.lower() == 'çıkış':
                break
            try:
                repo_index = int(repo_index) - 1
                if 0 <= repo_index < len(repos):
                    repo = repos[repo_index]
                    clone_repository(repo['html_url'], repo['name'])
                else:
                    console.print("[bold red]Geçersiz numara. Lütfen tekrar deneyin.[/bold red]")
            except ValueError:
                console.print("[bold red]Geçersiz giriş. Lütfen bir numara veya 'çıkış' girin.[/bold red]")
    else:
        console.print(f"[bold red]{search_date.strftime('%Y-%m-%d')} tarihinde yeni CVE bulunamadı.[/bold red]")


def main():
    setup()
    handle_existing_last_search_file()

    while True:
        menu = Panel.fit("""
[bold cyan]Ne yapmak istersiniz?[/bold cyan]
1. [bold yellow]Belirli bir CVE veya anahtar kelime ara[/bold yellow]
2. [bold yellow]Yeni CVE'leri ara[/bold yellow]
3. [bold yellow]Belirli bir tarihte oluşturulan CVE'leri ara[/bold yellow]
4. [bold yellow]Yardım[/bold yellow]
5. [bold yellow]Çıkış[/bold yellow]
""", title="[bold green]Menü[/bold green]", border_style="green")

        console.print(menu)

        try:
            choice = Prompt.ask("[bold cyan]Bir seçenek seçin[/bold cyan]", choices=[str(i) for i in range(1, 6)], default="1")
            if choice == "1":
                search_term = Prompt.ask("[bold yellow]Aramak istediğiniz CVE ID'sini veya anahtar kelimeyi girin[/bold yellow]")
                search_specific_cve_or_keyword(search_term)
            elif choice == "2":
                search_new_cves()
            elif choice == "3":
                search_cves_by_date()
            elif choice == "4":
                console.print("""
[bold cyan]Yardım - Mevcut Komutlar[/bold cyan]
1. [bold yellow]CVE ID'sini veya anahtar kelimeyi girerek belirli bir CVE'yi veya depoyu ara.[/bold yellow]
2. [bold yellow]Son aramadan beri oluşturulan yeni CVE'leri ara.[/bold yellow]
3. [bold yellow]Belirli bir tarihte oluşturulan CVE'leri ara.[/bold yellow]
4. [bold yellow]Programdan çık.[/bold yellow]
""")
            elif choice == "5":
                break
        except ValueError:
            console.print("[bold red]Geçersiz giriş. Lütfen 1 ile 5 arasında bir numara girin.[/bold red]")

if __name__ == "__main__":
    main()
