
```
xiaohongshu
├─ config
│  ├─ constants.py
│  ├─ settings.py
│  ├─ __init__.py
│  └─ __pycache__
│     ├─ constants.cpython-313.pyc
│     ├─ settings.cpython-313.pyc
│     └─ __init__.cpython-313.pyc
├─ data
│  ├─ logs
│  │  └─ crawler.log
│  ├─ processed
│  │  └─ comics
│  │     ├─ annotations.json
│  │     ├─ comic_001
│  │     │  ├─ images
│  │     │  └─ meta.json
│  │     └─ crawl_report.json
│  ├─ raw
│  └─ screenshots
│     ├─ 20260113_123446_https___www.baidu.com.png
│     ├─ 20260113_123544_https___www.baidu.com.png
│     ├─ note_20260113_125722_6587b9c2.png
│     ├─ note_20260113_130041_6587b9c2.png
│     ├─ note_20260113_130322_694e4d72.png
│     ├─ note_20260113_130335_694fc565.png
│     ├─ note_20260113_130349_695b2301.png
│     ├─ note_20260113_130404_6955591b.png
│     ├─ note_20260113_130416_69401190.png
│     ├─ note_20260113_130429_694a5d80.png
│     ├─ note_20260113_130628_6949c377.png
│     ├─ note_20260113_130642_69531979.png
│     ├─ note_20260113_130656_69512598.png
│     ├─ note_20260113_130735_6946650d.png
│     ├─ note_20260113_130749_695ecc7c.png
│     ├─ note_20260113_130803_69566d4b.png
│     ├─ search_20260113_125709_外卖翻车.png
│     ├─ search_20260113_130015_外卖翻车.png
│     ├─ search_20260113_130308_外卖翻车.png
│     └─ search_20260113_130614_点餐翻车.png
├─ requirements.txt
├─ scripts
│  ├─ quick_test.py
│  ├─ run_crawler.py
│  └─ setup.py
├─ src
│  ├─ crawler
│  │  ├─ parser.py
│  │  ├─ request_handler.py
│  │  ├─ selenium_handler.py
│  │  ├─ xhs_crawler.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ parser.cpython-313.pyc
│  │     ├─ request_handler.cpython-313.pyc
│  │     ├─ selenium_handler.cpython-313.pyc
│  │     ├─ xhs_crawler.cpython-313.pyc
│  │     └─ __init__.cpython-313.pyc
│  ├─ main.py
│  ├─ processor
│  │  ├─ data_filter.py
│  │  ├─ image_processor.py
│  │  ├─ text_processor.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ data_filter.cpython-313.pyc
│  │     └─ __init__.cpython-313.pyc
│  ├─ storage
│  │  ├─ data_manager.py
│  │  ├─ json_formatter.py
│  │  └─ __init__.py
│  ├─ utils
│  │  ├─ helper.py
│  │  ├─ logger.py
│  │  ├─ validator.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ helper.cpython-313.pyc
│  │     ├─ logger.cpython-313.pyc
│  │     ├─ validator.cpython-313.pyc
│  │     └─ __init__.cpython-313.pyc
│  ├─ __init__.py
│  └─ __pycache__
│     └─ __init__.cpython-313.pyc
├─ target.txt
├─ testlog.txt
├─ tests
│  ├─ test_crawler.py
│  ├─ test_login.py
│  ├─ test_processor.py
│  ├─ test_selenium.py
│  ├─ test_storage.py
│  ├─ test_utils.py
│  └─ __init__.py
├─ test_note_page.html
└─ test_search_page.html

```
```
xiaohongshu
├─ .wdm
│  ├─ drivers
│  │  └─ chromedriver
│  │     └─ win64
│  │        └─ 143.0.7499.192
│  │           ├─ chromedriver-win32
│  │           │  ├─ chromedriver.exe
│  │           │  ├─ LICENSE.chromedriver
│  │           │  └─ THIRD_PARTY_NOTICES.chromedriver
│  │           └─ chromedriver-win32.zip
│  └─ drivers.json
├─ chromedriver.exe
├─ config
│  ├─ constants.py
│  ├─ settings.py
│  ├─ __init__.py
│  └─ __pycache__
│     ├─ constants.cpython-313.pyc
│     ├─ settings.cpython-313.pyc
│     └─ __init__.cpython-313.pyc
├─ data
│  ├─ logs
│  │  └─ crawler.log
│  ├─ processed
│  │  └─ comics
│  │     ├─ annotations.json
│  │     ├─ comic_001
│  │     │  ├─ images
│  │     │  └─ meta.json
│  │     └─ crawl_report.json
│  ├─ raw
│  └─ screenshots
│     ├─ 20260113_123446_https___www.baidu.com.png
│     ├─ 20260113_123544_https___www.baidu.com.png
│     ├─ note_20260113_125722_6587b9c2.png
│     ├─ note_20260113_130041_6587b9c2.png
│     ├─ note_20260113_130322_694e4d72.png
│     ├─ note_20260113_130335_694fc565.png
│     ├─ note_20260113_130349_695b2301.png
│     ├─ note_20260113_130404_6955591b.png
│     ├─ note_20260113_130416_69401190.png
│     ├─ note_20260113_130429_694a5d80.png
│     ├─ note_20260113_130628_6949c377.png
│     ├─ note_20260113_130642_69531979.png
│     ├─ note_20260113_130656_69512598.png
│     ├─ note_20260113_130735_6946650d.png
│     ├─ note_20260113_130749_695ecc7c.png
│     ├─ note_20260113_130803_69566d4b.png
│     ├─ search_20260113_125709_外卖翻车.png
│     ├─ search_20260113_130015_外卖翻车.png
│     ├─ search_20260113_130308_外卖翻车.png
│     └─ search_20260113_130614_点餐翻车.png
├─ debug_selenium.py
├─ install_chromedriver.py
├─ LICENSE.chromedriver
├─ README.md
├─ requirements.txt
├─ scripts
│  ├─ quick_test.py
│  ├─ run_crawler.py
│  └─ setup.py
├─ src
│  ├─ .wdm
│  │  ├─ drivers
│  │  │  └─ chromedriver
│  │  │     └─ win64
│  │  │        └─ 143.0.7499.192
│  │  │           ├─ chromedriver-win32
│  │  │           │  ├─ chromedriver.exe
│  │  │           │  ├─ LICENSE.chromedriver
│  │  │           │  └─ THIRD_PARTY_NOTICES.chromedriver
│  │  │           └─ chromedriver-win32.zip
│  │  └─ drivers.json
│  ├─ crawler
│  │  ├─ parser.py
│  │  ├─ request_handler.py
│  │  ├─ selenium_handler.py
│  │  ├─ xhs_crawler.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ parser.cpython-313.pyc
│  │     ├─ request_handler.cpython-313.pyc
│  │     ├─ selenium_handler.cpython-313.pyc
│  │     ├─ xhs_crawler.cpython-313.pyc
│  │     └─ __init__.cpython-313.pyc
│  ├─ main.py
│  ├─ processor
│  │  ├─ data_filter.py
│  │  ├─ image_processor.py
│  │  ├─ text_processor.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ data_filter.cpython-313.pyc
│  │     └─ __init__.cpython-313.pyc
│  ├─ storage
│  │  ├─ data_manager.py
│  │  ├─ json_formatter.py
│  │  └─ __init__.py
│  ├─ utils
│  │  ├─ helper.py
│  │  ├─ logger.py
│  │  ├─ validator.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ helper.cpython-313.pyc
│  │     ├─ logger.cpython-313.pyc
│  │     ├─ validator.cpython-313.pyc
│  │     └─ __init__.cpython-313.pyc
│  ├─ __init__.py
│  └─ __pycache__
│     └─ __init__.cpython-313.pyc
├─ target.txt
├─ testchromeloginlog.txt
├─ testerrorlog.txt
├─ tests
│  ├─ test_crawler.py
│  ├─ test_login.py
│  ├─ test_processor.py
│  ├─ test_selenium.py
│  ├─ test_storage.py
│  ├─ test_utils.py
│  └─ __init__.py
├─ test_login_page.html
├─ test_login_success.png
├─ test_note_page.html
├─ test_search_page.html
├─ THIRD_PARTY_NOTICES.chromedriver
└─ xiaohongshu_cookies.json

```