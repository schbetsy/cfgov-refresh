import nose
from nose.plugins.attrib import attr

from selenose.cases import SeleniumTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from .test_helpers import *

class NewsroomTestCase(SeleniumTestCase):
    def setUp(self):
        self.driver.get('http://refresh.demo.cfpb.gov/newsroom/')
        # self.filter_dropdown_button = self.driver.find_element_by_xpath('//button[contains(text(), "Filter posts")]')
        click_filter_posts(self)

    def test_filter_display_button(self):
        filter_options = self.driver.find_element_by_class_name('padded-container')
        assert filter_options.is_displayed()

    @attr('checkbox')
    def test_filter_checkboxes(self):
        categoryList = ["Op-Ed", "Press Release", "Speech", "Testimony", "Blog"]
        for cat in categoryList:
            # use this after view changes value of checkbox input to 'Blog'
            # checkbox = self.driver.find_element_by_xpath('//label/input[@value=\"'+ cat +'\"]/..')
            checkbox = self.driver.find_element_by_xpath('//label/span[contains(text(), \"'+ cat +'\")]/..')
            checkbox.click()
            assert "is-checked" in checkbox.get_attribute('class')
            checkbox.click()
            assert "is-checkedFocus" in checkbox.get_attribute('class')

    @attr('search')
    @attr('category')
    def test_filter_category_search(self):
        categoryList = ["Op-Ed", "Press Release", "Speech", "Testimony"] # No Blog posts yet so add in when data is there
        for cat in categoryList:
            click_filter_posts(self)
            # checkbox = self.driver.find_element_by_xpath('//label/span[contains(text(), \"'+ cat +'\")]/..')
            checkbox = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//label/span[contains(text(), \"'+ cat +'\")]/..'))
            )
            checkbox.click()
            filter_results_button = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//input[@value="Apply filters"]'))
            )
            filter_results_button.click()
            cat = coerce_category_for_dom(cat)
            cat_type_elem = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//a[@href="?filter_category='+ cat +'"]'))
            )
            assert cat_type_elem
            click_filter_posts(self)
            cat = coerce_category_for_dom(cat)
            # checkbox = self.driver.find_element_by_xpath('//label/span[contains(text(), \"'+ cat +'\")]/..')
            checkbox = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//label/span[contains(text(), \"'+ cat +'\")]/..'))
            )
            checkbox.click()

if __name__ == '__main__':
   nose.main()
