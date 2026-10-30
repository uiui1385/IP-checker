import flet as ft
import requests

def main(page: ft.Page):
    page.title = "IP Resolver - @tariknet_pv"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    header = ft.Column(
        controls=[
            ft.Text(
                "🌐 Website IP Resolver",
                size=26,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.CYAN_ACCENT,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                "Developed by: @tariknet_pv",
                size=14,
                weight=ft.FontWeight.W_500,
                color=ft.colors.LIGHT_BLUE_200,
                text_align=ft.TextAlign.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    url_input = ft.TextField(
        label="دامنه یا آدرس سایت (مثلاً google.com)",
        hint_text="example.com",
        prefix_icon=ft.icons.LINK,
        border_radius=12,
        autofocus=True,
    )

    status_text = ft.Text(value="", size=14, text_align=ft.TextAlign.CENTER)

    result_column = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def resolve_domain(domain: str, record_type: str):
        try:
            url = f"https://cloudflare-dns.com/dns-query?name={domain}&type={record_type}"
            headers = {"accept": "application/dns-json"}
            res = requests.get(url, headers=headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                if "Answer" in data:
                    return [item["data"] for item in data["Answer"] if item.get("data")]
        except Exception:
            pass
        return []

    def copy_to_clipboard(e):
        page.set_clipboard(e.control.data)
        page.snack_bar = ft.SnackBar(ft.Text("آدرس IP کپی شد! ✅"), duration=1500)
        page.snack_bar.open = True
        page.update()

    def on_check_clicked(e):
        raw_val = (url_input.value or "").strip().lower()
        if not raw_val:
            status_text.value = "لطفاً ابتدا نام یک دامنه را وارد کنید."
            status_text.color = ft.colors.RED_ACCENT
            result_column.controls.clear()
            page.update()
            return

        domain = raw_val.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]

        status_text.value = "در حال دریافت اطلاعات DNS..."
        status_text.color = ft.colors.AMBER_ACCENT
        result_column.controls.clear()
        page.update()

        ipv4_list = resolve_domain(domain, "A")
        ipv6_list = resolve_domain(domain, "AAAA")

        result_column.controls.clear()

        if not ipv4_list and not ipv6_list:
            status_text.value = "هیچ رکوردی برای این دامنه پیدا نشد یا ارتباط با DNS برقرار نشد."
            status_text.color = ft.colors.RED_ACCENT
            page.update()
            return

        status_text.value = f"نتایج مربوط به {domain}:"
        status_text.color = ft.colors.GREEN_ACCENT

        for ip in ipv4_list:
            result_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.icons.DNS, color=ft.colors.CYAN_300),
                            ft.Text(f"IPv4: {ip}", size=15, weight=ft.FontWeight.BOLD, expand=True),
                            ft.IconButton(
                                icon=ft.icons.COPY,
                                tooltip="کپی",
                                data=ip,
                                on_click=copy_to_clipboard,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    padding=10,
                    border_radius=10,
                )
            )

        for ip in ipv6_list:
            result_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.icons.DNS, color=ft.colors.PURPLE_200),
                            ft.Text(f"IPv6: {ip}", size=13, weight=ft.FontWeight.BOLD, expand=True),
                            ft.IconButton(
                                icon=ft.icons.COPY,
                                tooltip="کپی",
                                data=ip,
                                on_click=copy_to_clipboard,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    padding=10,
                    border_radius=10,
                )
            )

        page.update()

    check_btn = ft.ElevatedButton(
        text="دریافت آی‌پی (Resolve IP)",
        icon=ft.icons.SEARCH,
        style=ft.ButtonStyle(
            color=ft.colors.BLACK,
            bgcolor=ft.colors.CYAN_ACCENT,
            padding=15,
        ),
        on_click=on_check_clicked,
    )

    footer = ft.Container(
        content=ft.TextButton(
            text="پشتیبانی و ارتباط: @tariknet_pv",
            icon=ft.icons.SEND,
            url="https://t.me/tariknet_pv",
        ),
        margin=ft.margin.only(top=30),
    )

    page.add(
        header,
        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
        url_input,
        ft.Container(content=check_btn, margin=ft.margin.only(top=10, bottom=10)),
        status_text,
        result_column,
        footer,
    )
