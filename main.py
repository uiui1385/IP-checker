import flet as ft
from flet import app
import requests
from urllib.parse import urlparse

def clean_domain(raw_input: str) -> str:
    raw_input = raw_input.strip()
    if raw_input.startswith("http://") or raw_input.startswith("https://"):
        raw_input = urlparse(raw_input).netloc
    # حذف پورت یا اسلش‌های اضافی
    raw_input = raw_input.split('/')[0].split(':')[0].strip()
    return raw_input

def resolve_dns(domain: str):
    """استعلام رکوردهای A و AAAA از طریق Cloudflare DNS over HTTPS"""
    results = {"A": [], "AAAA": []}
    headers = {"accept": "application/dns-json"}
    
    for record_type in ["A", "AAAA"]:
        try:
            url = f"https://cloudflare-dns.com/dns-query?name={domain}&type={record_type}"
            res = requests.get(url, headers=headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                for ans in data.get("Answer", []):
                    # نوع 1 = A و نوع 28 = AAAA
                    if ans.get("type") in [1, 28]:
                        results[record_type].append(ans.get("data"))
        except Exception:
            pass
            
    results["A"] = sorted(list(set(results["A"])))
    results["AAAA"] = sorted(list(set(results["AAAA"])))
    return results

def main(page: ft.Page):
    page.title = "DNS & IP Resolver Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # اسنک‌بار برای اعلان کپی شدن
    def show_toast(text: str):
        page.snack_bar = ft.SnackBar(ft.Text(text, color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True
        page.update()

    # دیالوگ سازنده (About)
    def open_about(e):
        about_dialog = ft.AlertDialog(
            title=ft.Text("درباره توسعه‌دهنده", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.Text("ابزار استعلام پیشرفته IP و DNS سایت‌ها"),
                    ft.Text("توسعه یافته توسط:"),
                    ft.TextButton(
                        text="@tariknet_pv",
                        icon=ft.Icons.TELEGRAM,
                        url="https://t.me/tariknet_pv"
                    ),
                ],
                tight=True,
                spacing=10
            ),
            actions=[
                ft.TextButton("بستن", on_click=lambda _: page.close(about_dialog))
            ]
        )
        page.open(about_dialog)

    # هدر بالای برنامه
    header = ft.Row(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.SECURITY, color=ft.Colors.CYAN_ACCENT, size=28),
                    ft.Text("IP Resolver Pro", size=22, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.IconButton(
                icon=ft.Icons.INFO_OUTLINE,
                tooltip="درباره ما",
                on_click=open_about,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # فیلد ورودی دامنه
    txt_domain = ft.TextField(
        label="آدرس دامنه یا سایت",
        hint_text="example.com",
        prefix_icon=ft.Icons.LANGUAGE,
        border_radius=12,
        expand=True,
    )

    # لیست نتایج
    result_list = ft.ListView(expand=True, spacing=10, padding=5)
    progress_bar = ft.ProgressBar(visible=False, color=ft.Colors.CYAN_ACCENT)

    def create_ip_card(ip: str, ip_type: str):
        def copy_click(e):
            page.set_clipboard(ip)
            show_toast(f"آی‌پی {ip} با موفقیت کپی شد!")

        return ft.Card(
            elevation=4,
            content=ft.Container(
                padding=12,
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(ip, size=15, weight=ft.FontWeight.BOLD, selectable=True),
                                ft.Text(f"نوع رکورد: {ip_type}", size=11, color=ft.Colors.GREY_400),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.COPY_ROUNDED,
                            tooltip="کپی آی‌پی",
                            on_click=copy_click,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
        )

    def on_search(e):
        raw_val = txt_domain.value
        domain = clean_domain(raw_val)
        if not domain:
            show_toast("لطفاً آدرس یک دامنه را بنویسید!")
            return

        progress_bar.visible = True
        btn_search.disabled = True
        result_list.controls.clear()
        page.update()

        try:
            data = resolve_dns(domain)
            v4_list = data["A"]
            v6_list = data["AAAA"]

            if not v4_list and not v6_list:
                result_list.controls.append(
                    ft.Text("هیچ آی‌پی یا رکوردی برای این آدرس پیدا نشد.", color=ft.Colors.RED_ACCENT)
                )
            else:
                if v4_list:
                    result_list.controls.append(
                        ft.Text(f"آدرس‌های IPv4 ({len(v4_list)} مورد):", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_200)
                    )
                    for ip in v4_list:
                        result_list.controls.append(create_ip_card(ip, "IPv4 (A)"))

                if v6_list:
                    result_list.controls.append(
                        ft.Text(f"آدرس‌های IPv6 ({len(v6_list)} مورد):", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_200)
                    )
                    for ip in v6_list:
                        result_list.controls.append(create_ip_card(ip, "IPv6 (AAAA)"))

        except Exception as err:
            result_list.controls.append(ft.Text(f"خطا در دریافت اطلاعات: {err}", color=ft.Colors.RED_400))

        progress_bar.visible = False
        btn_search.disabled = False
        page.update()

    btn_search = ft.ElevatedButton(
        "استعلام IP",
        icon=ft.Icons.SEARCH,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.CYAN_700,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        height=50,
        on_click=on_search,
    )

    # فوتر ثابت شامل آیدی تلگرام
    footer = ft.Container(
        padding=10,
        content=ft.Row(
            [
                ft.Text("Dev Support:", size=12, color=ft.Colors.GREY_400),
                ft.TextButton(
                    text="@tariknet_pv",
                    url="https://t.me/tariknet_pv",
                    style=ft.ButtonStyle(color=ft.Colors.CYAN_ACCENT),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

    page.add(
        header,
        ft.Divider(opacity=0.3),
        ft.Row([txt_domain, btn_search]),
        progress_bar,
        ft.Container(content=result_list, expand=True),
        ft.Divider(opacity=0.2),
        footer,
    )

if __name__ == "__main__":
    ft.app(target=main)
