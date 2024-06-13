import asyncio
import re
import sys
from playwright.async_api import Playwright, async_playwright, expect

class AutoWebDataTable:
    def __init__(self, url, include_txt, except_txt):
        self.entryUrl = url
        self.row_include_text = include_txt
        self.row_except_text = except_txt

    def get_page_bar(self, page, page_index):
        return page.locator(".el-pager li").filter(has_text=re.compile(rf"\s*{page_index}\s*"))

    async def run(self, playwright: Playwright) -> None:
        # playwright.chromium.launch(channel="chrome", executable_path="D:/Software/.local-chromium/chrome.exe", headless=False, args=["--start-maximized"])
        browser = await playwright.chromium.launch(channel="msedge", headless=False, args=["--start-maximized"])
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()
        await page.goto(self.entryUrl)
        await page.get_by_placeholder("用户名").click()
        await page.get_by_placeholder("用户名").fill("admin")
        await page.get_by_placeholder("用户名").press("Tab")
        await page.get_by_placeholder("密码").fill("123456")
        await page.get_by_placeholder("密码").press("Enter")
        await page.wait_for_load_state(state='networkidle')
        await page.wait_for_timeout(200)
        page_index = 1
        page_url = page.url
        page_bar = self.get_page_bar(page, page_index)
        last_page_index = int((await page.locator(".el-pager li").last.text_content()).strip())

        while True:
            page_records = await page.locator(f".el-table__body-wrapper table > tbody > tr").all()
            handing_records = []
            activeRecordTextContents = []
            for i in range(len(page_records)):
                # 观察检查表格每一行是否符合预期(如果页面存在动画, 动画还未结束的时候页面上的元素可能跟最终的页面结构不一致)
                # await page_records[i].highlight()
                # await page.wait_for_timeout(500)
                recordRecordText = await page_records[i].text_content()
                if self.row_except_text and self.row_except_text in recordRecordText:
                    continue
                if self.row_include_text and self.row_include_text not in recordRecordText:
                    continue
                if '处理中' not in recordRecordText:
                    continue
                
                if len(activeRecordTextContents) == 0 or recordRecordText not in activeRecordTextContents: 
                    handing_records.append(i + 1)
                    activeRecordTextContents.append(recordRecordText)
            print(handing_records)
            for index in handing_records:
                # 每次进入列表页面, 要确保页码正确
                await page_bar.click()

                # 高亮当前要处理的行
                await page_records[index - 1].highlight()
                
                # 等待页面加载动画
                await page.wait_for_timeout(200)

                # 等待网络处于空闲状态, 并且出现了需要处理的表格行
                await page.wait_for_load_state(state='networkidle')
                selector = f".approve-render .el-table__fixed-body-wrapper > .el-table__body > tbody > tr:nth-child({index}) button"

                await page.locator(selector).click(force=True)
                # 等待页面加载动画
                await page.wait_for_timeout(200)
                
                # 等待网络处于空闲状态, 并且出现了需要点击的按钮
                await page.wait_for_load_state(state='networkidle')
                await page.wait_for_selector("tr:has-text('处理中')")
                
                # 表格中找到"处理中"的所在行, 点击删除按钮, 确定
                handing_row = page.locator("tr:has-text('处理中')")
                stepName = await handing_row.locator("td:nth-child(2) > .cell").text_content()
                await handing_row.locator("button:has-text('删除任务')").click()
                await page.get_by_role("button", name="确定").click()
                # 激活步骤
                await page.locator("button:has-text('激活步骤')").click()
                await page.get_by_placeholder("请选择").click()
                await page.locator(f"li:has-text('{stepName}')").click()
                await page.locator("button:has-text('激活此任务')").click()
                await page.get_by_role("button", name="确定").click()
                await page.goto(page_url)

            page_index += 1
            if page_index > last_page_index:
                break
            else:
                page_bar = self.get_page_bar(page, page_index)
                await page_bar.click()
                await page.wait_for_timeout(500)
                page_url = page.url
            
        await page.pause()

        # ---------------------
        await context.close()
        await browser.close()

async def main(entry_url, include_txt, except_txt) -> None:
    auto_datable = AutoWebDataTable(entry_url, include_txt, except_txt)
    async with async_playwright() as playwright:
        await auto_datable.run(playwright)


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 3:
        entry_url = args[1]
        include_txt = args[2]
        except_txt = ''
        if len(args) == 4:
            except_txt = args[3]
    asyncio.run(main(entry_url, include_txt, except_txt))
