import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from .objects import Experience, Education, Scraper, Interest, Accomplishment, Contact
import os
from linkedin_scraper import selectors
import time


class Person(Scraper):

    __TOP_CARD = "pv-top-card"
    __WAIT_FOR_ELEMENT_TIMEOUT = 100

    def __init__(
        self,
        linkedin_url=None,
        name=None,
        experiences=None,
        educations=None,
        interests=None,
        accomplishments=None,
        company=None,
        job_title=None,
        contacts=None,
        driver=None,
        get=True,
        scrape=True,
        close_on_complete=True,
        time_to_wait_after_login=0,
    ):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about = ""
        self.experiences = experiences or []
        self.educations = educations or []
        self.interests = interests or []
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []
        self.company_urls = []
        self.company_details = []
        self.skills = []
        self.languages = []
        self.phone = ""
        self.email = ""
        self.address = ""
        self.location = ""

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        if scrape:
            self.scrape(close_on_complete)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("you are not logged in!")

    def _click_see_more_by_class_name(self, class_name):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            div = self.driver.find_element(By.CLASS_NAME, class_name)
            div.find_element(By.TAG_NAME, "button").click()
        except Exception as e:
            pass

    def is_open_to_work(self):
        try:
            return "#OPEN_TO_WORK" in self.driver.find_element(By.CLASS_NAME,"pv-top-card-profile-picture").find_element(By.TAG_NAME,"img").get_attribute("title")
        except:
            return False

    def get_experiences(self):
        url = os.path.join(self.linkedin_url, "details/experience")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list", base=main)
        if main_list is not None:
            for position in main_list.find_elements(By.XPATH,"li"):
                no_experience = self.driver.find_elements(By.CLASS_NAME, "artdeco-empty-state")
                if len(no_experience) == 1:
                    break
                position = position.find_element(By.CLASS_NAME,"pvs-entity")
                company_logo_elem, position_details = position.find_elements(By.XPATH,"*")

                # company elem
                company_linkedin_url = company_logo_elem.find_element(By.XPATH,"*").get_attribute("href")
                self.company_urls.append(company_linkedin_url)

                # position details
                position_details_list = position_details.find_elements(By.XPATH,"*")
                position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
                outer_positions = position_summary_details.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")

                commitment = ""
                work_times = None
                from_date = None
                to_date = None
                duration = None
                location = None
                commitment = None

                if len(outer_positions) == 4:
                    position_title = outer_positions[0].find_element(By.TAG_NAME,"span").text
                    company = outer_positions[1].find_element(By.TAG_NAME,"span").text
                    if "·" in company:
                        commitment = company.split(" · ")[1]
                        company = company.split(" · ")[0]
                    work_times = outer_positions[2].find_element(By.TAG_NAME,"span").text
                    location = outer_positions[3].find_element(By.TAG_NAME,"span").text
                elif len(outer_positions) == 3:
                    if "·" in outer_positions[2].text:
                        position_title = outer_positions[0].find_element(By.TAG_NAME,"span").text
                        company = outer_positions[1].find_element(By.TAG_NAME,"span").text
                        if "·" in company:
                            commitment = company.split(" · ")[1]
                            company = company.split(" · ")[0]
                        work_times = outer_positions[2].find_element(By.TAG_NAME,"span").text
                        location = ""
                    else:
                        position_title = ""
                        company = outer_positions[0].find_element(By.TAG_NAME,"span").text
                        if "·" in company:
                            commitment = company.split(" · ")[1]
                            company = company.split(" · ")[0]
                        work_times = outer_positions[1].find_element(By.TAG_NAME,"span").text
                        location = outer_positions[2].find_element(By.TAG_NAME,"span").text
                elif len(outer_positions) == 2:
                    second_line = outer_positions[1].find_element(By.TAG_NAME,"span").text
                    if " - " in second_line:
                        company = outer_positions[0].find_element(By.TAG_NAME,"span").text
                        if "·" in company:
                            commitment = company.split(" · ")[1]
                            company = company.split(" · ")[0]
                        work_times = outer_positions[1].find_element(By.TAG_NAME,"span").text
                    else:
                        position_title = outer_positions[0].find_element(By.TAG_NAME,"span").text
                        company = outer_positions[1].find_element(By.TAG_NAME,"span").text

                times = work_times.split("·")[0].strip() if work_times else ""
                duration = work_times.split("·")[1].strip() if work_times and len(work_times.split("·")) > 1 else None

                if " - " in times:
                    from_date = "".join(times.split(" - ")[0]) if times else ""
                    to_date = "".join(times.split(" - ")[1]) if times else ""

                temp = position_summary_text.find_element(By.CLASS_NAME,"pvs-list").find_elements(By.CLASS_NAME,"pvs-list") if position_summary_text else None

                if position_summary_text is None:
                    experience = Experience(
                        position_title=position_title,
                        from_date=from_date if from_date else "",
                        to_date=to_date if to_date else "",
                        duration=duration if duration else "",
                        location=location,
                        institution_name=company,
                        linkedin_url=company_linkedin_url,
                        commitment=commitment
                    )
                    self.add_experience(experience)
                # the following elif controls the positions which are in the same company and follow each other, i.e. a list of positions in a company
                elif position_summary_text and temp is not None and len(temp) > 0 and len(temp[0].find_elements(By.XPATH,"li")) > 1:
                    descriptions = position_summary_text.find_element(By.CLASS_NAME,"pvs-list").find_element(By.CLASS_NAME,"pvs-list").find_elements(By.XPATH,"li")
                    for description in descriptions:
                        temp_desc = ""
                        skills = []
                        res = description.find_element(By.TAG_NAME,"a").find_elements(By.XPATH,"*")
                        position_title_elem = res[0].find_element(By.TAG_NAME,"span").text
                        work_times_elem = None
                        location_elem = None
                        if len(res) == 4:
                            commitment = res[1].find_element(By.XPATH,"*").text
                            work_times_elem = res[2] if len(res) > 2 else None
                            location_elem = res[3] if len(res) > 3 else None
                        elif len(res) == 3:
                            if "·" in res[1].find_element(By.XPATH,"*").text:
                                work_times_elem = res[1]
                                location_elem = res[2]
                            elif "·" in res[2].find_element(By.XPATH,"*").text:
                                commitment = res[1].find_element(By.XPATH,"*").text
                                work_times_elem = res[2]
                        elif len(res) == 2:
                            if "·" in res[1].find_element(By.XPATH,"*").text:
                                work_times_elem = res[1]

                        temp = description.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")[1].find_elements(By.XPATH,"*")[1].find_elements(By.XPATH,"*")
                        if len(temp) > 1:
                            temp1 = temp[1].find_element(By.XPATH,"*").find_elements(By.XPATH,"*")
                            if len(temp1) > 1:
                                temp_desc = temp1[0].find_element(By.TAG_NAME,"span").text
                                skills = temp1[1].find_element(By.TAG_NAME,"span").text[8:].split("·")
                                skills = [skills.strip() for skills in skills]
                            elif len(temp1) == 1:
                                text = temp1[0].find_element(By.TAG_NAME,"span").text
                                if text.startswith("Skills:"):
                                    skills = text[8:].split("·")
                                    skills = [skills.strip() for skills in skills]
                                else:
                                    temp_desc = text

                        location = location_elem.find_element(By.XPATH,"*").text if location_elem else None
                        position_title = position_title_elem
                        work_times = work_times_elem.find_element(By.XPATH,"*").text if work_times_elem else ""
                        times = work_times.split("·")[0].strip() if work_times else ""
                        duration = work_times.split("·")[1].strip() if len(work_times.split("·")) > 1 else None
                        from_date = " ".join(times.split(" ")[:2]) if times else ""
                        to_date = " ".join(times.split(" ")[3:]) if times else ""

                        experience = Experience(
                            position_title=position_title,
                            from_date=from_date,
                            to_date=to_date,
                            duration=duration,
                            location=location,
                            description=temp_desc,
                            institution_name=company,
                            linkedin_url=company_linkedin_url,
                            skills=skills,
                            commitment=commitment
                        )
                        self.add_experience(experience)
                else:
                    temp = position_summary_text.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")
                    skills = []
                    temp_desc = ""
                    if len(temp) > 1:
                        temp_desc = temp[0].find_element(By.TAG_NAME,"span").text
                        skills = temp[1].find_element(By.TAG_NAME,"span").text[8:].split("·")
                        skills = [skills.strip() for skills in skills]
                    elif len(temp) == 1:
                        text = temp[0].find_element(By.TAG_NAME,"span").text
                        if text.startswith("Skills:"):
                            skills = text[8:].split("·")
                            skills = [skills.strip() for skills in skills]
                        else:
                            temp_desc = text

                    experience = Experience(
                        position_title=position_title,
                        from_date=from_date,
                        to_date=to_date,
                        duration=duration,
                        location=location,
                        description=temp_desc,
                        institution_name=company,
                        linkedin_url=company_linkedin_url,
                        skills=skills,
                        commitment=commitment
                    )
                    self.add_experience(experience)

    def get_company_details(self):
        for url in self.company_urls:
            if url is not None and "linkedin.com/company" in url:
                self.driver.get(url + '/about/')
                self.focus()
                WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until( lambda driver:
                    driver.find_elements(By.CLASS_NAME,"artdeco-empty-state") or
                    driver.find_elements(By.CLASS_NAME,"org-unclaimable-page-module") or
                    driver.find_elements(By.TAG_NAME,"main")
                )
                unavailable = self.driver.find_elements(By.CLASS_NAME, "artdeco-empty-state")
                if len(unavailable) == 1:
                    continue
                main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
                unclaimed = self.driver.find_elements(By.CLASS_NAME, "org-unclaimable-page-module")
                if len(unclaimed) == 1:
                    continue
                header = main.find_elements(By.XPATH, "*")[0].find_element(By.CLASS_NAME, "ember-view").find_element(By.CLASS_NAME, "ph5")
                info = header.find_elements(By.XPATH, "*")[0].find_elements(By.XPATH, "*")[1].find_element(By.XPATH, "*")
                institution_name = info.find_element(By.TAG_NAME, "h1").text
                description = info.find_elements(By.TAG_NAME, "p")
                institution_description = ''
                website = ''
                industry = ''
                institution_followers = ''
                institution_employees = ''
                institution_location = ''
                if len(description) == 1:
                    institution_description = info.find_element(By.TAG_NAME, "p").text
                company_summary = info.find_element(By.TAG_NAME, "div").find_elements(By.XPATH, "*")
                if len(company_summary) > 1:
                    industry = company_summary[0].text
                    company_summary_points = company_summary[1].find_elements(By.XPATH, "*")
                    for element in company_summary_points:
                        if "followers" in element.text:
                            institution_followers = element.text.split(" ")[0]
                        elif "employees" in element.text:
                            institution_employees = element.text.split(" ")[0]
                        else:
                            institution_location = element.text
                elif len(company_summary) == 1:
                    company_summary_points = company_summary[0].find_elements(By.XPATH, "*")
                    for element in company_summary_points:
                        if "followers" in element.text:
                            institution_followers = element.text.split(" ")[0]
                        elif "employees" in element.text:
                            institution_employees = element.text.split(" ")[0]
                        else:
                            institution_location = element.text
                website = ''
                size = ''
                specialties = []
                overview = main.find_elements(By.XPATH, "*")[1].find_element(By.XPATH, "*").find_elements(By.XPATH, "*")[0].find_elements(By.XPATH, "*")[0].find_element(By.XPATH, "*")
                institution_overivew = overview.find_elements(By.TAG_NAME, 'p')
                if len(institution_overivew) == 1:
                    institution_overivew = institution_overivew[0].text
                overview_item_headers = overview.find_element(By.TAG_NAME, "dl").find_elements(By.TAG_NAME, "dt")
                overview_item_texts = overview.find_element(By.TAG_NAME, "dl").find_elements(By.TAG_NAME, "dd")
                if len(overview_item_headers) > 1:
                    for index, header in enumerate(overview_item_headers):
                        if 'Website' in header.text:
                            website = overview_item_texts[index].text
                        elif 'Company size' in header.text:
                            size = overview_item_texts[index].text
                    if 'Specialties' in overview_item_headers[-1].text:
                        specialties = overview_item_texts[-1].text.split(', ')
                        if specialties[-1].startswith("and "):
                            specialties[-1] = specialties[-1][4:]
                side = self.wait_for_element_to_load(by=By.ID, name="org-right-rail")
                funding = side.find_elements(By.CLASS_NAME, "org-funding__card-spacing")
                funding_title = ''
                funding_series = ''
                funding_date = ''
                funding_amount = ''
                if len(funding) == 1:
                    funding_elements = funding[0].find_elements(By.XPATH, "*")
                    funding_title = funding_elements[0].find_elements(By.XPATH, "*")[0].text
                    funding_rounds = funding_elements[0].find_elements(By.XPATH, "*")[1].text
                    funding_details = funding_elements[3].find_elements(By.XPATH, "*")[0].text
                    funding_series = ' '.join(funding_details.split(" ")[:-3])
                    funding_date = ' '.join(funding_details.split(" ")[-3:])
                    if len(funding_elements[3].find_elements(By.XPATH, "*")) > 1:
                        funding_amount = funding_elements[3].find_elements(By.XPATH, "*")[1].text
                    if "Investors" in funding_elements[4].find_elements(By.XPATH, "*")[0].text:
                        funding_investors = funding_elements[4].find_elements(By.XPATH, "*")[1].find_element(By.XPATH, "*").find_elements(By.XPATH, "*")
                for experience in self.experiences:
                    if url == experience.linkedin_url:
                        experience.institution_description = institution_description
                        experience.institution_overivew = institution_overivew
                        experience.industry = industry
                        experience.institution_followers = institution_followers
                        experience.institution_employees = institution_employees
                        experience.institution_location = institution_location
                        experience.website = website
                        experience.size = size
                        experience.specialties = specialties
                        experience.funding_title = funding_title
                        experience.funding_series = funding_series
                        experience.funding_date = funding_date
                        experience.funding_amount = funding_amount

    def get_educations(self):
        url = os.path.join(self.linkedin_url, "details/education")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()

        main_list = self.wait_for_element_to_load(name="pvs-list", base=main)
        if main_list is not None:
            for position in main_list.find_elements(By.CLASS_NAME,"pvs-entity"):
                institution_logo_elem, position_details = position.find_elements(By.XPATH,"*")

                # company elem
                institution_linkedin_url = institution_logo_elem.find_element(By.XPATH,"*").get_attribute("href")

                # position details
                position_details_list = position_details.find_elements(By.XPATH,"*")
                position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
                outer_positions = position_summary_details.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")

                institution_name = outer_positions[0].find_element(By.TAG_NAME,"span").text
                major = ""
                degree = ""
                from_date = None
                to_date = None
                if len(outer_positions) > 1:
                    degree = outer_positions[1].find_element(By.TAG_NAME,"span").text

                    if "Degree, " in degree:
                        major = degree.split("Degree, ")[1]
                        degree = degree.split(major)[0][:-2]

                    if len(outer_positions) > 2:
                        times = outer_positions[2].find_element(By.TAG_NAME,"span").text

                        from_date = " ".join(times.split(" ")[:1])
                        to_date = " ".join(times.split(" ")[2:])

                description = ""
                if position_summary_text and len(position_summary_text.find_elements(By.TAG_NAME,"span")) > 0:
                    description = position_summary_text.find_element(By.TAG_NAME,"span").text

                education = Education(
                    from_date=from_date,
                    to_date=to_date,
                    description=description,
                    degree=degree,
                    institution_name=institution_name,
                    linkedin_url=institution_linkedin_url,
                    major=major
                )
                self.add_education(education)

    def get_skills(self):
        url = os.path.join(self.linkedin_url, "details/skills")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME,name="main")
        time.sleep(1)
        no_skills = main.find_elements(By.CLASS_NAME,"artdeco-empty-state")
        if len(no_skills) == 0:
            skill_list = self.wait_for_element_to_load(name="pvs-list", base=main)
            self.scroll_to_bottom()
            WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR,".artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--full.artdeco-button--secondary.ember-view.scaffold-finite-scroll__load-button"))
            )
            # need to wait for at least a second since the absence of the button above doesn't mean the missing skills are loaded
            time.sleep(1)
            skill_list = main.find_element(By.CLASS_NAME,"pvs-list").find_elements(By.XPATH,"*")
            for skill_info in skill_list:
                skill = skill_info.find_element(By.TAG_NAME,"a").find_element(By.TAG_NAME,"span").text
                self.skills.append(skill)

    def get_languages(self):
        url = os.path.join(self.linkedin_url, "details/languages")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        no_languages = self.driver.find_elements(By.CLASS_NAME, "artdeco-empty-state")
        if len(no_languages) == 0:
            language_list = self.wait_for_element_to_load(name="pvs-list", base=main)
            for language_info in language_list.find_elements(By.CLASS_NAME,"pvs-entity"):
                language = language_info.find_element(By.TAG_NAME,"span").text
                self.languages.append(language)

    def get_name_and_location(self):
        top_panels = self.driver.find_elements(By.CLASS_NAME,"pv-text-details__left-panel")
        self.name = top_panels[0].find_elements(By.XPATH,"*")[0].find_element(By.TAG_NAME,"h1").text
        self.location = top_panels[1].find_elements(By.XPATH,"*")[0].text

    def get_contact_info(self):
        contact_info_span = self.driver.find_element(By.ID,"top-card-text-details-contact-info")
        contact_info_span.click()
        contact_info = self.wait_for_element_to_load(by=By.CLASS_NAME, name="section-info")
        for info in contact_info.find_elements(By.XPATH,"*"):
            if "ci-phone" in info.get_attribute("class"):
                self.phone = info.find_element(By.TAG_NAME,"span").text
            elif "ci-address" in info.get_attribute("class"):
                self.address = info.find_element(By.TAG_NAME,"a").text
            elif "ci-email" in info.get_attribute("class"):
                self.email = info.find_element(By.TAG_NAME,"a").text
        close_contact_info = self.driver.find_element(By.CLASS_NAME,"artdeco-modal__dismiss")
        close_contact_info.click()

    def get_about(self):
        about_section = self.driver.find_elements(By.ID,"about")
        if len(about_section) == 1:
            about_section = about_section[0]
            self.about = about_section.find_element(By.XPATH,"..").find_element(By.CLASS_NAME,"display-flex").find_element(By.TAG_NAME,"span").text

    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        duration = None

        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    self.__TOP_CARD,
                )
            )
        )
        self.focus()
        self.wait(2)

        self.get_name_and_location()

        self.open_to_work = self.is_open_to_work()

        self.get_about()

        self.get_contact_info()

        self.get_experiences()

        self.get_company_details()

        self.get_educations()

        self.get_skills()

        self.get_languages()

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "<Person {name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nCompanies\n{companies}\n\nLanguages\n{lang}\n\nSkills\n{skills}>".format(
            name=self.name,
            about=self.about,
            email=self.email,
            address=self.address,
            phone=self.phone,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            lang=self.languages,
            skills=self.skills
        )
