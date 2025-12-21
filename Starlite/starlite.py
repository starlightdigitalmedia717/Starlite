import sys
import json
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QLineEdit, QAction, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        
        # Create first tab
        self.add_new_tab(QUrl('https://www.google.com'), 'New Tab')
        
        self.showMaximized()
        self.setWindowTitle('Starlite 💫')
        
        # Navigation Bar
        nav_toolbar = QToolBar()
        self.addToolBar(nav_toolbar)
        
        #Bookmarks Bar
        self.bookmarks_toolbar = QToolBar()
        self.addToolBar(self.bookmarks_toolbar)
        
        self.bookmarks = self.load_bookmarks()
        self.update_bookmarks_bar()
        tabs_toolbar = QToolBar()
        self.addToolBar(tabs_toolbar)
        
        # Add tab management buttons
        new_tab_btn = QAction('New Tab', self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab(QUrl('https://www.google.com'), 'New Tab'))
        tabs_toolbar.addAction(new_tab_btn)

        self.add_button(nav_toolbar, '🔙', self.current_browser.back)
        self.add_button(nav_toolbar, '⏩', self.current_browser.forward)
        self.add_button(nav_toolbar, '🔄️', self.current_browser.reload)

        add_bookmark_btn = QAction('★', self)
        add_bookmark_btn.setToolTip('Bookmark this page')
        add_bookmark_btn.triggered.connect(self.toggle_bookmark)

        nav_toolbar.addAction(add_bookmark_btn)
        self.bookmark_star = add_bookmark_btn

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_bar)

        # Connect tab change signal after url_bar is created
        self.tabs.currentChanged.connect(self.update_navigation)
        self.tabs.currentChanged.connect(self.update_bookmark_star)

        self.update_navigation()
        self.update_bookmark_star()
    
    def add_button(self, nav_toolbar, text, action):
        forward_btn = QAction(text, self)
        forward_btn.triggered.connect(action)
        nav_toolbar.addAction(forward_btn)

    @property
    def current_browser(self):
        return self.tabs.currentWidget()

    def add_new_tab(self, url, title):
        browser = QWebEngineView()
        browser.setUrl(url)
        browser.urlChanged.connect(lambda url, browser=browser: self.update_tab_title(browser, url))
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(browser, title=title))
        
        index = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def update_tab_title(self, browser, url=None, title=None):
        index = self.tabs.indexOf(browser)
        if title:
            self.tabs.setTabText(index, title)
        elif url:
            self.tabs.setTabText(index, url.toString())

    def update_navigation(self):
        browser = self.current_browser
        if browser:
            self.url_bar.setText(browser.url().toString())
            try:
                browser.urlChanged.disconnect(self.update_url_bar)
            except:
                pass
            browser.urlChanged.connect(self.update_url_bar)
            browser.urlChanged.connect(self.update_bookmark_star)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url # Basic http prefix handling
        self.current_browser.setUrl(QUrl(url))

    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())

    def load_bookmarks(self):
        bookmarks_file = 'bookmarks.json'
        if os.path.exists(bookmarks_file):
            with open(bookmarks_file, 'r') as f:
                return json.load(f)
        return []

    def save_bookmarks(self):
        with open('bookmarks.json', 'w') as f:
            json.dump(self.bookmarks, f)

    def toggle_bookmark(self):
        browser = self.current_browser
        url = browser.url().toString()
        
        # Check if already bookmarked
        existing_bookmark = next((b for b in self.bookmarks if b['url'] == url), None)
        
        if existing_bookmark:
            # Remove bookmark
            self.bookmarks.remove(existing_bookmark)
            self.save_bookmarks()
            self.update_bookmarks_bar()
        else:
            # Add bookmark
            title = browser.page().title()
            self.bookmarks.append({'title': title, 'url': url})
            self.save_bookmarks()
            self.update_bookmarks_bar()
        
        self.update_bookmark_star()

    def update_bookmark_star(self):
        browser = self.current_browser
        if browser:
            url = browser.url().toString()
            is_bookmarked = any(b['url'] == url for b in self.bookmarks)
            
            if is_bookmarked:
                self.bookmark_star.setText('⭐')
                self.bookmark_star.setToolTip('Remove bookmark')
            else:
                self.bookmark_star.setText('★')
                self.bookmark_star.setToolTip('Bookmark this page')

    def update_bookmarks_bar(self):
        self.bookmarks_toolbar.clear()
        for bookmark in self.bookmarks:
            action = QAction(bookmark['title'], self)
            action.triggered.connect(lambda checked, url=bookmark['url']: self.navigate_to_bookmark(url))
            self.bookmarks_toolbar.addAction(action)

    def navigate_to_bookmark(self, url):
        self.current_browser.setUrl(QUrl(url))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleBrowser()
    sys.exit(app.exec_())
