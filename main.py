import asyncio
import flet as ft
import requests


async def main(page: ft.Page):
    page.title = "IP Resolver - @tariknet_pv"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    header_icon = ft.Icon(
        ft.Icons.PODCAST_ROUNDED,
        size=48,
        color="#00E5FF",
    )

    header_title = ft.Text(
        "IP Finder Pro",
        size=22,
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF",
    )

    badge = ft.Container(
        content=ft.Text(
            "Created by @tariknet_pv",
            size=12,
            weight=ft.FontWeight.W_600,
            color="#80DEEA",
        ),
        bgcolor="#004D40",
        padding=ft.padding.symmetric(horizontal=12, vertical=5),
        border_radius=20,
    )

    domain_input = ft.TextField(
        label="آدرس دامنه یا سایت",
        hint_text="مثال: google.com",
        prefix_icon=ft.Icons.LANGUAGE,
        border_radius=12,
        border_color="#00E5FF",
        text_align=ft.TextAlign.LEFT,
    )

    loading = ft.ProgressRing(visible=False, color="#00E5FF")

    result_text = ft.Text(
        "",
        size=14,
        selectable=True,
        color="#FFFFFF",
    )

    result_card = ft.Card(
        content=ft.Container(
            content=result_text,
            padding=16,
            width=350,
        ),
        visible=False,
        color="#1E1E1E",
    )

    def clean_domain(raw_url: str) -> str:
        url = raw_url.strip().lower()
        if "://" in url:
            url = url.split("://", 1)[1]
        url = url.split("/")[0]
        url = url.split(":")[0]
        return url

    async def fetch_ip(e):
        target = clean_domain(domain_input.value or "")
        if not target:
            result_text.value = "⚠️ لطفاً یک نام دامنه یا آدرس وارد کنید."
            result_card.visible = True
            await page.update_async()
            return

        loading.visible = True
        result_card.visible = False
        await page.update_async()

        loop = asyncio.get_running_loop()

        def query_dns():
            ips = []
            try:
                url_a = f"https://cloudflare-dns.com/dns-query?name={target}&type=A"
                res_a = requests.get(url_a, headers={"accept": "application/dns-json"}, timeout=8).json()
                if "Answer" in res_a:
                    for record in res_a["Answer"]:
                        if record.get("type") == 1:
                            ips.append(("IPv4", record.get("data")))
            except Exception:
                pass

            try:
                url_aaaa = f"https://cloudflare-dns.com/dns-query?name={target}&type=AAAA"
                res_aaaa = requests.get(url_aaaa, headers={"accept": "application/dns-json"}, timeout=8).json()
                if "Answer" in res_aaaa:
                    for record in res_aaaa["Answer"]:
                        if record.get("type") == 28:
                            ips.append(("IPv6", record.get("data")))
            except Exception:
                pass
            return ips

        found_ips = await loop.run_in_executor(None, query_dns)

        if found_ips:
            output = f"🌐 نتایج برای دامنه: {target}\n"
            output += "═" * 28 + "\n\n"
            for ip_type, ip_val in found_ips:
                output += f"📍 [{ip_type}]: {ip_val}\n"
            output += "\n━━━━━━━━━━━━━━━━━━\n"
            output += "Powered by: @tariknet_pv"
            result_text.value = output
        else:
            result_text.value = f"❌ هیچ آی‌پی برای '{target}' پیدا نشد یا اینترنت قطع است."

        loading.visible = False
        result_card.visible = True
        await page.update_async()

    btn_search = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SEARCH, color="#000000"),
                ft.Text("دریافت آی‌پی", size=15, weight=ft.FontWeight.BOLD, color="#000000"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
        style=ft.ButtonStyle(
            bgcolor="#00E5FF",
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(vertical=14, horizontal=25),
        ),
        on_click=fetch_ip,
        width=220,
    )

    footer = ft.Container(
        content=ft.Column(
            [
                ft.Divider(color="#424242"),
                ft.Text(
                    "پشتیبانی و ارتباط تلگرام: tariknet_pv@",
                    size=12,
                    color="#9E9E9E",
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        margin=ft.margin.only(top=30),
    )

    await page.add_async(
        ft.Container(height=10),
        header_icon,
        header_title,
        badge,
        ft.Container(height=20),
        domain_input,
        ft.Container(height=15),
        btn_search,
        ft.Container(height=15),
        loading,
        result_card,
        footer,
    )


if __name__ == "__main__":
    try:
        from flet_runtime.app import app_async
        asyncio.run(app_async(main))
    except Exception:
        ft.app(main)
