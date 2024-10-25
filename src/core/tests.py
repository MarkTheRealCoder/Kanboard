
import unittest
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestAuthAcceptance(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.wait = WebDriverWait(self.driver, 5)
        self.server_url = "http://localhost:8000/"
        self.dummy_username = "acceptancetest"
        self.dummy_password = "acceptancetest"
        self.dummy_email = "acceptance@test.com"
        self.dummy_name = "Acceptance"
        self.dummy_surname = "Test"
        self.dummy_board = "Acceptance Board"
        self.dummy_column_title = "Test Column"
        self.dummy_column_description = "Test Column Description"
        self.dummy_card_title = "Test Card"
        self.dummy_card_description = "Test Card Description"
        self.dummy_card_story_points = "5"
        self.dummy_card_column = 0
        self.dummy_card_date_expire = "2024-12-24"

    def tearDown(self):
        driver = self.driver
        try:
            driver.get(self.server_url + 'acceptance/delete/')
        except Exception as e:
            print(f"Cleanup failed: {e}")
        finally:
            self.driver.close()
            print("Test completed.")

    def test_register(self):
        driver = self.driver
        driver.get(self.server_url + 'register')
        self.assertEqual("Kanboard - Register", driver.title)

        name = driver.find_element(By.ID, "name")
        surname = driver.find_element(By.ID, "surname")
        username = driver.find_element(By.ID, "username")
        email = driver.find_element(By.ID, "email")
        password = driver.find_element(By.ID, "password")
        repeat_password = driver.find_element(By.ID, "repeat-password")
        submit = driver.find_element(By.CLASS_NAME, "submit-button")

        name.send_keys(self.dummy_name)
        surname.send_keys(self.dummy_surname)
        username.send_keys(self.dummy_username)
        email.send_keys(self.dummy_email)
        password.send_keys(self.dummy_password)
        repeat_password.send_keys(self.dummy_password)
        submit.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "dashboard")))
        except NoSuchElementException as e:
            self.fail(f"Register failed: {e}")

        self.assertIsNotNone(result)
        self.assertEqual("Kanboard - Dashboard", driver.title)

    def test_login(self):
        try:
            self.test_logout()
        except Exception:
            print("[INFO] Could not logout")

        driver = self.driver
        driver.get(self.server_url + 'login')
        self.assertEqual("Kanboard - Log In", driver.title)

        email = driver.find_element(By.ID, "email")
        password = driver.find_element(By.ID, "password")
        submit = driver.find_element(By.CLASS_NAME, "submit-button")

        email.send_keys(self.dummy_email)
        password.send_keys(self.dummy_password)
        submit.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "dashboard")))
        except NoSuchElementException as e:
            self.fail(f"Login failed: {e}")

        self.assertIsNotNone(result)
        self.assertEqual("Kanboard - Dashboard", driver.title)

    def test_logout(self):
        try:
            self.test_register()
        except Exception:
            print("[INFO] Could not register")

        driver = self.driver
        driver.get(self.server_url + 'dashboard')

        result = None

        try:
            result = self.wait.until(EC.element_to_be_clickable((By.ID, "logout")))
        except NoSuchElementException as e:
            self.fail(f"Logout failed: {e}")

        result.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Logout failed: {e}")

        self.assertIsNotNone(result)
        self.assertEqual("Kanboard - Log In", driver.title)

    def test_create_board(self):
        try:
            self.test_login()
        except Exception:
            print("[INFO] Could not login")

        driver = self.driver
        driver.get(self.server_url + 'dashboard')

        result = None

        try:
            result = self.wait.until(EC.element_to_be_clickable((By.ID, "add-board")))
        except NoSuchElementException as e:
            self.fail(f"Create board failed: {e}")

        result.click()

        try:
            board_title = self.wait.until(EC.presence_of_element_located((By.ID, "board_title")))
        except NoSuchElementException as e:
            self.fail(f"Create board failed: {e}")

        board_title.send_keys(self.dummy_board)
        submit = driver.find_element(By.ID, "create")
        submit.click()

        try:
            result = self.wait.until(EC.element_to_be_clickable((By.ID, "add-column")))
        except NoSuchElementException as e:
            self.fail(f"Create board failed: {e}")

        self.assertIsNotNone(result)
        self.assertEqual("Kanboard - " + self.dummy_board, driver.title)

    def test_open_board(self):
        try:
            self.test_create_board()
        except Exception:
            print("[INFO] Could not create board")

        driver = self.driver
        driver.get(self.server_url + 'dashboard')

        result = None

        try:
            result = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "board-silhouette")))
        except NoSuchElementException as e:
            self.fail(f"Open board failed: {e}")

        classes = driver.find_elements(By.CLASS_NAME, "board-silhouette")
        self.assertIsNotNone(classes)

        board_to_click = classes[0]
        board_to_click.click()

        try:
            result = self.wait.until(EC.element_to_be_clickable((By.ID, "add-column")))
        except NoSuchElementException as e:
            self.fail(f"Open board failed: {e}")

        self.assertIsNotNone(result)
        self.assertEqual("Kanboard - " + self.dummy_board, driver.title)

    def test_create_column(self):
        try:
            self.test_open_board()
        except Exception:
            print("[INFO] Could not open board")

        driver = self.driver

        add_column = driver.find_element(By.ID, "add-column")
        self.assertIsNotNone(add_column)

        add_column.click()

        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create column failed: {e}")

        column_title = driver.find_element(By.ID, "column_title")
        column_description = driver.find_element(By.ID, "column_description")
        create_button = driver.find_element(By.ID, "create")

        column_title.send_keys(self.dummy_column_title)
        column_description.send_keys(self.dummy_column_description)
        create_button.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "modable")))
        except NoSuchElementException as e:
            self.fail(f"Create column failed: {e}")

        self.assertIsNotNone(result)
        self.assertEqual("Kanboard - " + self.dummy_board, driver.title)

    def test_create_card(self):
        try:
            self.test_create_column()
        except Exception:
            print("[INFO] Could not create column")

        driver = self.driver

        add_card = driver.find_element(By.ID, "add-card")
        self.assertIsNotNone(add_card)

        add_card.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        self.assertIsNotNone(result)

        card_title = driver.find_element(By.ID, "card_title")
        card_description = driver.find_element(By.ID, "card_description")
        card_column = driver.find_element(By.ID, "column")
        card_date = driver.find_element(By.ID, "expiration_date")
        card_story_points = driver.find_element(By.ID, "story_points")
        create_button = driver.find_element(By.ID, "create")

        card_title.send_keys(self.dummy_card_title)
        card_description.send_keys(self.dummy_card_description)

        select = Select(card_column)
        select.select_by_index(self.dummy_card_column)

        card_date.send_keys(self.dummy_card_date_expire)

        card_story_points.send_keys(self.dummy_card_story_points)
        create_button.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-silhouette")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        self.assertIsNotNone(result)
        self.assertEqual("Kanboard - " + self.dummy_board, driver.title)

    def test_burndown(self):
        try:
            self.test_open_board()
        except Exception:
            print("[INFO] Could not open board")

        driver = self.driver

        burndown = driver.find_element(By.ID, "burndown")
        self.assertIsNotNone(burndown)

        burndown.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "burndown")))
        except NoSuchElementException as e:
            self.fail(f"Burndown failed: {e}")

        self.assertIsNotNone(result)
        self.assertEqual("Kanboard - Burndown", driver.title)

    def test_manage_users(self):
        try:
            self.test_open_board()
        except Exception:
            print("[INFO] Could not open board")

        driver = self.driver

        add_user = driver.find_element(By.ID, "add-user")
        self.assertIsNotNone(add_user)

        add_user.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        self.assertIsNotNone(result)

        assigned_users = driver.find_element(By.ID, "assigned-users")
        kanboard_users = driver.find_element(By.ID, "kanboard-users")
        create = driver.find_element(By.ID, "create")

        user_kanboard_users = kanboard_users.find_elements(By.CLASS_NAME, "user-field")[0]
        user_kanboard_users.click()

        create.click()

        sleep(2)
        driver.find_element(By.ID, "service-message").click()
        sleep(2)

        add_user.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        self.assertIsNotNone(result)

        assigned_users = driver.find_element(By.ID, "assigned-users")
        self.assertIsNotNone(assigned_users)
        user_assigned_users = assigned_users.find_elements(By.CLASS_NAME, "user-field")[0]
        self.assertIsNotNone(user_assigned_users)

        create = driver.find_element(By.ID, "create")
        create.click()

        sleep(2)
        driver.find_element(By.ID, "service-message").click()
        sleep(2)

        #
        # Repeat for remove user
        #
        add_user.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        self.assertIsNotNone(result)

        assigned_users = driver.find_element(By.ID, "assigned-users")
        kanboard_users = driver.find_element(By.ID, "kanboard-users")
        create = driver.find_element(By.ID, "create")

        user_assigned_users = assigned_users.find_elements(By.CLASS_NAME, "user-field")[0]
        user_assigned_users.click()

        create.click()

        sleep(2)
        driver.find_element(By.ID, "service-message").click()
        sleep(2)

        add_user.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        self.assertIsNotNone(result)

        kanboard_users = driver.find_element(By.ID, "kanboard-users")
        self.assertIsNotNone(kanboard_users)
        user_kanboard_users = kanboard_users.find_elements(By.CLASS_NAME, "user-field")[0]
        self.assertIsNotNone(user_kanboard_users)

    def test_modify_card(self):
        try:
            self.test_create_card()
        except Exception:
            print("[INFO] Could not create card")

        driver = self.driver

        card = driver.find_element(By.CLASS_NAME, "card-silhouette")
        self.assertIsNotNone(card)

        card.find_element(By.TAG_NAME, "h4").click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "delete-card")))
        except NoSuchElementException as e:
            self.fail(f"Modify card failed: {e}")

        self.assertIsNotNone(result)

        title = driver.find_element(By.ID, "card_title")
        description = driver.find_element(By.ID, "card_description")
        story_points = driver.find_element(By.ID, "story_points")
        expiration_date = driver.find_element(By.ID, "expiration_date")
        completed = driver.find_element(By.ID, "completed")
        assignee = driver.find_element(By.CLASS_NAME, "assignees").find_elements(By.CLASS_NAME, "input-field")[0]
        confirm_card = driver.find_element(By.ID, "confirm-card")

        title.clear()
        title.send_keys(self.dummy_card_title)

        description.clear()
        description.send_keys(self.dummy_card_description)

        story_points.clear()
        story_points.send_keys(self.dummy_card_story_points)

        expiration_date.clear()
        expiration_date.send_keys(self.dummy_card_date_expire)

        completed.click()

        assignee.click()

        confirm_card.click()

        sleep(2)

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-silhouette")))
        except NoSuchElementException as e:
            self.fail(f"Modify card failed: {e}")

        self.assertIsNotNone(result)

        result = result.find_element(By.CLASS_NAME, "card-assignees").find_element(By.TAG_NAME, "img")

        self.assertIsNotNone(result)


    def test_delete_card(self):
        try:
            self.test_create_card()
        except Exception:
            print("[INFO] Could not create card")

        driver = self.driver

        card = driver.find_element(By.CLASS_NAME, "card-silhouette")
        self.assertIsNotNone(card)

        card.find_element(By.TAG_NAME, "h4").click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "delete-card")))
        except NoSuchElementException as e:
            self.fail(f"Delete card failed: {e}")

        self.assertIsNotNone(result)

        delete_card = driver.find_element(By.ID, "delete-card")

        delete_card.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "warning-advisory")))
        except NoSuchElementException as e:
            self.fail(f"Delete card failed: {e}")

        self.assertIsNotNone(result)

        confirm_delete = driver.find_element(By.ID, "confirm-dangerous-action")
        confirm_delete.click()
        sleep(2)

        self.assertRaises(NoSuchElementException, lambda: driver.find_element(By.CLASS_NAME, "card-silhouette"))


    def test_modify_column(self):
        try:
            self.test_create_column()
        except Exception:
            print("[INFO] Could not create column")

        driver = self.driver

        column = driver.find_element(By.CLASS_NAME, "column-silhouette")
        self.assertIsNotNone(column)

        column.find_element(By.TAG_NAME, "h2").click()

        try:
            result = self.wait.until(EC.visibility_of_element_located((By.ID, "column-modal-panel")))
        except NoSuchElementException as e:
            self.fail(f"Modify column failed: {e}")

        self.assertIsNotNone(result)

        column_description = result.find_element(By.ID, "column_description")
        column_title = result.find_element(By.ID, "column_title")
        confirm_column = result.find_element(By.ID, "confirm-column")

        column_title.clear()
        column_title.send_keys(self.dummy_column_title)

        column_description.clear()
        column_description.send_keys(self.dummy_column_description)

        confirm_column.click()

        sleep(1)

        try:
            result = self.wait.until(EC.visibility_of_element_located((By.ID, "service-message")))
        except NoSuchElementException as e:
            self.fail(f"Modify column failed: {e}")

        self.assertIsNotNone(result)


    def test_delete_column(self):
        try:
            self.test_create_column()
        except Exception:
            print("[INFO] Could not create column")

        driver = self.driver

        column = driver.find_element(By.CLASS_NAME, "column-silhouette")
        self.assertIsNotNone(column)

        actions = ActionChains(driver)
        actions.move_to_element(column).perform()

        try:
            result = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "deleting-button")))
        except NoSuchElementException as e:
            self.fail(f"Delete column failed: {e}")

        self.assertIsNotNone(result)

        result.click()

        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "confirm-dangerous-action")))
        except NoSuchElementException as e:
            self.fail(f"Delete column failed: {e}")

        self.assertIsNotNone(result)

        result.click()

        sleep(1)

        self.assertRaises(NoSuchElementException, lambda: driver.find_element(By.CLASS_NAME, "column-silhouette"))


    def test_move_card(self):
        driver = self.driver

        try:
            self.test_create_card()

            add_card = driver.find_element(By.ID, "add-card")
            self.assertIsNotNone(add_card)

            add_card.click()

            try:
                result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
            except NoSuchElementException as e:
                self.fail(f"Create card failed: {e}")

            self.assertIsNotNone(result)

            card_title = driver.find_element(By.ID, "card_title")
            card_description = driver.find_element(By.ID, "card_description")
            card_column = driver.find_element(By.ID, "column")
            card_date = driver.find_element(By.ID, "expiration_date")
            card_story_points = driver.find_element(By.ID, "story_points")
            create_button = driver.find_element(By.ID, "create")

            card_title.send_keys("ToBeFirst")
            card_description.send_keys(self.dummy_card_description)

            select = Select(card_column)
            select.select_by_index(self.dummy_card_column)

            card_date.send_keys(self.dummy_card_date_expire)

            card_story_points.send_keys(self.dummy_card_story_points)
            create_button.click()

            try:
                result = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card-silhouette + .card-silhouette")))
            except NoSuchElementException as e:
                self.fail(f"Create card failed: {e}")

            self.assertIsNotNone(result)
            self.assertEqual("Kanboard - " + self.dummy_board, driver.title)
        except Exception:
            print("[INFO] Could not create card")


        card, card2 = driver.find_elements(By.CLASS_NAME, "card-silhouette")
        card = card.find_element(By.TAG_NAME, "p")
        sleep(1)
        actions = ActionChains(driver)
        actions.move_to_element(card).click_and_hold(card).move_by_offset(0, 400) \
            .move_to_element_with_offset(card2, 0, 50).release().perform()
        sleep(1)

        try:
            result = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".card-silhouette + .card-silhouette + #dnd-placeholder")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        self.assertIsNotNone(result)


    def test_move_column(self):
        driver = self.driver

        try:
            self.test_create_column()

            add_column = driver.find_element(By.ID, "add-column")
            self.assertIsNotNone(add_column)

            add_column.click()

            try:
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
            except NoSuchElementException as e:
                self.fail(f"Create column failed: {e}")

            column_title = driver.find_element(By.ID, "column_title")
            column_description = driver.find_element(By.ID, "column_description")
            create_button = driver.find_element(By.ID, "create")

            column_title.send_keys("ToBeFirst")
            column_description.send_keys(self.dummy_column_description)
            create_button.click()

            try:
                result = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modable + .modable")))
            except NoSuchElementException as e:
                self.fail(f"Create column failed: {e}")
        except Exception:
            print("[INFO] Could not create card")


        column, column2 = driver.find_elements(By.CLASS_NAME, "column-silhouette")
        column = column.find_element(By.TAG_NAME, "p")
        sleep(1)
        actions = ActionChains(driver)
        actions.drag_and_drop_by_offset(column, 500, 0).perform()
        sleep(1)

        try:
            result = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modable + .modable + #dnd-placeholder")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        self.assertIsNotNone(result)




if __name__ == "__main__":
    unittest.main()
