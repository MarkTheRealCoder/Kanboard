
import unittest
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
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
        """
        Tests the registration functionality on the '/register' page.

        Ensures that a user can fill out the registration form, submit it,
        and be redirected to the dashboard upon successful registration.
        """

        driver = self.driver
        driver.get(self.server_url + 'register')

        # Checks that the page title is correct, confirming the page loaded as expected
        self.assertEqual("Kanboard - Register", driver.title)

        # Locates the register form elements by their IDs
        name = driver.find_element(By.ID, "name")
        surname = driver.find_element(By.ID, "surname")
        username = driver.find_element(By.ID, "username")
        email = driver.find_element(By.ID, "email")
        password = driver.find_element(By.ID, "password")
        repeat_password = driver.find_element(By.ID, "repeat-password")
        submit = driver.find_element(By.CLASS_NAME, "submit-button")

        # Populate each form field with dummy data
        name.send_keys(self.dummy_name)
        surname.send_keys(self.dummy_surname)
        username.send_keys(self.dummy_username)
        email.send_keys(self.dummy_email)
        password.send_keys(self.dummy_password)
        repeat_password.send_keys(self.dummy_password)

        # Click the submit button to register
        submit.click()

        # Waits for the dashboard element to appear as a sign of successful registration
        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "dashboard")))
        except NoSuchElementException as e:
            self.fail(f"Register failed: {e}")

        # Verifies that the title of the page is now the dashboard title, indicating successful redirection
        self.assertEqual("Kanboard - Dashboard", driver.title)


    def test_login(self):
        """
        Tests the login functionality on the '/login' page.

        Ensures that a user can fill out the login form, submit it,
        and be redirected to the dashboard upon successful login.
        """

        # Attempts to log out before testing login to ensure a fresh session
        try:
            self.test_logout()
        except Exception:
            print("[INFO] Could not logout")

        driver = self.driver
        driver.get(self.server_url + 'login')

        # Checks that the page title is correct, confirming the page loaded as expected
        self.assertEqual("Kanboard - Log In", driver.title)

        # Locates the login form elements by their IDs
        email = driver.find_element(By.ID, "email")
        password = driver.find_element(By.ID, "password")
        submit = driver.find_element(By.CLASS_NAME, "submit-button")

        # Populates the form fields with the dummy user credentials
        email.send_keys(self.dummy_email)
        password.send_keys(self.dummy_password)

        # Click the submit button to log in
        submit.click()

        # Waits for the dashboard element to appear as a sign of successful login
        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "dashboard")))
        except NoSuchElementException as e:
            self.fail(f"Login failed: {e}")

        # Verifies that the title of the page is now the dashboard title, indicating successful redirection
        self.assertEqual("Kanboard - Dashboard", driver.title)


    def test_logout(self):
        """
        Tests the logout functionality on the 'dashboard' page.

        Ensures that a logged-in user can log out and be redirected to the login page.
        """

        # Attempts to register before testing logout to ensure the user is logged in
        try:
            self.test_register()
        except Exception:
            print("[INFO] Could not register")

        driver = self.driver
        driver.get(self.server_url + 'dashboard')

        result = None

        # Waits for the logout button to become clickable on the dashboard
        try:
            result = self.wait.until(EC.element_to_be_clickable((By.ID, "logout")))
        except NoSuchElementException as e:
            self.fail(f"Logout failed: {e}")

        # Clicks the logout button
        result.click()

        # Waits for the login form title element to appear, indicating a successful logout
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Logout failed: {e}")

        # Verifies that the title of the page is now the login page title, indicating successful redirection
        self.assertEqual("Kanboard - Log In", driver.title)


    def test_create_board(self):
        """
        Tests the board creation functionality on the 'dashboard' page.

        Ensures that a user can access the board creation form, fill in a title,
        submit it, and be redirected to the new board's page upon successful creation.
        """

        # Attempts to log in before testing board creation to ensure user is authenticated
        try:
            self.test_login()
        except Exception:
            print("[INFO] Could not login")

        driver = self.driver
        driver.get(self.server_url + 'dashboard')

        result = None

        # Waits for the "Add Board" button to become clickable on the dashboard
        try:
            result = self.wait.until(EC.element_to_be_clickable((By.ID, "add-board")))
        except NoSuchElementException as e:
            self.fail(f"Create board failed: {e}")

        # Clicks the "Add Board" button to open the board creation form
        result.click()

        # Waits for the board title input field to appear
        try:
            board_title = self.wait.until(EC.presence_of_element_located((By.ID, "board_title")))
        except NoSuchElementException as e:
            self.fail(f"Create board failed: {e}")

        # Enters the dummy board title into the input field
        board_title.send_keys(self.dummy_board)
        # Locates and clicks the "Create" button to submit the new board form
        submit = driver.find_element(By.ID, "create")
        submit.click()

        # Waits for the "Add Column" button to appear, indicating the board was created successfully
        try:
            result = self.wait.until(EC.element_to_be_clickable((By.ID, "add-column")))
        except NoSuchElementException as e:
            self.fail(f"Create board failed: {e}")

        # Verifies that the title of the page matches the new board's title, indicating successful creation
        self.assertEqual("Kanboard - " + self.dummy_board, driver.title)


    def test_open_board(self):
        """
        Tests the functionality to open an existing board from the 'dashboard' page.

        Ensures that a user can locate and click on a board from the dashboard,
        and be redirected to the board page upon successful selection.
        """

        # Attempts to create a board before testing the open board functionality to ensure a board exists
        try:
            self.test_create_board()
        except Exception:
            print("[INFO] Could not create board")

        driver = self.driver
        driver.get(self.server_url + 'dashboard')

        result = None

        # Waits for the board element to appear and become clickable on the dashboard
        try:
            result = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "board-silhouette")))
        except NoSuchElementException as e:
            self.fail(f"Open board failed: {e}")

        # Retrieves the list of boards displayed on the dashboard
        classes = driver.find_elements(By.CLASS_NAME, "board-silhouette")
        # Ensures that at least one board element was found
        self.assertIsNotNone(classes)

        # Clicks on the first board in the list to open it
        board_to_click = classes[0]
        board_to_click.click()

        # Waits for the "Add Column" button to appear on the board page, indicating it loaded successfully
        try:
            result = self.wait.until(EC.element_to_be_clickable((By.ID, "add-column")))
        except NoSuchElementException as e:
            self.fail(f"Open board failed: {e}")

        # Verifies that the title of the page matches the board's title, indicating successful navigation
        self.assertEqual("Kanboard - " + self.dummy_board, driver.title)


    def test_create_column(self):
        """
        Tests the column creation functionality within a board page.

        Ensures that a user can access the column creation form, fill out the details,
        submit it, and see the column added to the board upon successful creation.
        """

        # Attempts to open a board before testing column creation to ensure a board is available
        try:
            self.test_open_board()
        except Exception:
            print("[INFO] Could not open board")

        driver = self.driver

        # Locates the "Add Column" button on the board page
        add_column = driver.find_element(By.ID, "add-column")
        # Ensures that the "Add Column" button is present
        self.assertIsNotNone(add_column)

        # Clicks the "Add Column" button to open the column creation form
        add_column.click()

        # Waits for the form title element to appear, indicating the column creation form loaded
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create column failed: {e}")

        # Locates the column title and description fields, as well as the "Create" button
        column_title = driver.find_element(By.ID, "column_title")
        column_description = driver.find_element(By.ID, "column_description")
        create_button = driver.find_element(By.ID, "create")

        # Fills out the column title and description fields with dummy data
        column_title.send_keys(self.dummy_column_title)
        column_description.send_keys(self.dummy_column_description)
        # Clicks the "Create" button to submit the form and create the column
        create_button.click()

        # Waits for a column element to appear on the board page, indicating successful column creation
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "modable")))
        except NoSuchElementException as e:
            self.fail(f"Create column failed: {e}")

        # Verifies that the title of the page matches the board's title, indicating we are still on the board page
        self.assertEqual("Kanboard - " + self.dummy_board, driver.title)


    def test_create_card(self):
        """
        Tests the card creation functionality within a column on a board.

        Ensures that a user can access the card creation form, fill in the details,
        submit it, and see the card added to the column on the board upon successful creation.
        """

        # Attempts to create a column before testing card creation to ensure a column exists
        try:
            self.test_create_column()
        except Exception:
            print("[INFO] Could not create column")

        driver = self.driver

        # Locates the "Add Card" button in the dashboard page
        add_card = driver.find_element(By.ID, "add-card")
        # Ensures that the "Add Card" button is present
        self.assertIsNotNone(add_card)

        # Clicks the "Add Card" button to open the card creation form
        add_card.click()

        # Waits for the form title element to appear, indicating the card creation form loaded
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        # Locates the card form fields and the "Create" button by IDs
        card_title = driver.find_element(By.ID, "card_title")
        card_description = driver.find_element(By.ID, "card_description")
        card_column = driver.find_element(By.ID, "column")
        card_date = driver.find_element(By.ID, "expiration_date")
        card_story_points = driver.find_element(By.ID, "story_points")
        create_button = driver.find_element(By.ID, "create")

        # Fills in the card title and description fields with dummy data
        card_title.send_keys(self.dummy_card_title)
        card_description.send_keys(self.dummy_card_description)

        # Selects the appropriate column for the card using the dummy column index
        select = Select(card_column)
        select.select_by_index(self.dummy_card_column)

        # Enters the dummy expiration date and story points into the respective fields
        card_date.send_keys(self.dummy_card_date_expire)
        card_story_points.send_keys(self.dummy_card_story_points)

        # Clicks the "Create" button to submit the new card form
        create_button.click()

        # Waits for a card element to appear within the column, indicating successful card creation
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-silhouette")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        # Verifies that the title of the page matches the board's title, indicating we are still on the board page
        self.assertEqual("Kanboard - " + self.dummy_board, driver.title)


    def test_burndown(self):
        """
        Tests the burndown chart functionality within a board page.

        Ensures that a user can access the burndown chart for a project and
        verifies that the chart loads correctly on a new page.
        """

        # Attempts to open a board before testing the burndown functionality to ensure a board is available
        try:
            self.test_open_board()
        except Exception:
            print("[INFO] Could not open board")

        driver = self.driver

        # Locates the "Burndown" button on the board page
        burndown = driver.find_element(By.ID, "burndown")
        # Ensures that the "Burndown" button is present
        self.assertIsNotNone(burndown)

        # Clicks the "Burndown" button to open the burndown chart page
        burndown.click()

        # Waits for the burndown chart element to appear, indicating the chart page loaded successfully
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "burndown")))
        except NoSuchElementException as e:
            # The test fails if the burndown chart element does not appear
            self.fail(f"Burndown failed: {e}")

        # Verifies that the title of the page is the one of the Burndown,
        # indicating successful navigation to the chart page
        self.assertEqual("Kanboard - Burndown", driver.title)


    def test_manage_users(self):
        """
        Tests the user management functionality on a board.

        Ensures that a user can add and remove members from a board by navigating
        to the user management interface, selecting users, and submitting changes.
        """

        # Attempts to open a board before managing users to ensure a board is available
        try:
            self.test_open_board()
        except Exception:
            print("[INFO] Could not open board")

        driver = self.driver

        # Locates the "Add User" button
        add_user = driver.find_element(By.ID, "add-user")
        # Ensures that the "Add User" button is present
        self.assertIsNotNone(add_user)

        # Clicks the "Add User" button to access the user management form
        add_user.click()

        # Waits for the form title element to appear, indicating the user management form loaded
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        # Locates the "Assigned Users" and "Kanboard Users" sections in the form and the "Create" button
        assigned_users = driver.find_element(By.ID, "assigned-users")
        kanboard_users = driver.find_element(By.ID, "kanboard-users")
        create = driver.find_element(By.ID, "create")

        # Selects the first available user in the "Kanboard Users" list and assigns them to the board
        user_kanboard_users = kanboard_users.find_elements(By.CLASS_NAME, "user-field")[0]
        user_kanboard_users.click()

        # Clicks the "Create" button to assign the selected user
        create.click()

        # Waits for the service message to confirm the action, then dismisses it
        sleep(2)
        driver.find_element(By.ID, "service-message").click()
        sleep(2)

        # Re-opens the user management form by clicking "Add User" again
        add_user.click()

        # Waits for the form title element to appear again
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        # Locates the "Assigned Users" section to confirm the user was added
        assigned_users = driver.find_element(By.ID, "assigned-users")
        # Ensures that the "Assigned Users" section is present
        self.assertIsNotNone(assigned_users)

        # Retrieves the first user field within the "Assigned Users" section
        user_assigned_users = assigned_users.find_elements(By.CLASS_NAME, "user-field")[0]
        # Ensures that there is at least one user assigned
        self.assertIsNotNone(user_assigned_users)

        #
        # SECOND PART: Remove the user previously assigned from the Board.
        #

        # Re-assigns the user by clicking "Create" again, this time it will REMOVE the user from the board
        create = driver.find_element(By.ID, "create")
        create.click()

        # Waits for and dismisses the service message confirming the re-assignment
        sleep(2)
        driver.find_element(By.ID, "service-message").click()
        sleep(2)

        # Clicks on the button
        add_user.click()

        # Waits for the form title element to appear once more
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        # Locates the "Assigned Users" section
        assigned_users = driver.find_element(By.ID, "assigned-users")
        kanboard_users = driver.find_element(By.ID, "kanboard-users")
        create = driver.find_element(By.ID, "create")

        # Selects the first assigned user to remove
        user_assigned_users = assigned_users.find_elements(By.CLASS_NAME, "user-field")[0]
        user_assigned_users.click()

        # Clicks "Create" to remove the selected user from the board
        create.click()

        # Waits for and dismisses the service message confirming user removal
        sleep(2)
        driver.find_element(By.ID, "service-message").click()
        sleep(2)

        # Opens the user management form again to confirm the user removal
        add_user.click()

        # Waits for the form title element to appear again
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
        except NoSuchElementException as e:
            self.fail(f"Create card failed: {e}")

        # Locates the "Kanboard Users" section to confirm the user was removed
        assigned_users = driver.find_element(By.ID, "kanboard-users")
        # Ensures that the "Kanboard Users" section is present
        self.assertIsNotNone(assigned_users)

        # Retrieves the first user field within the "Kanboard Users" section
        user_assigned_users = assigned_users.find_elements(By.CLASS_NAME, "user-field")[0]
        # Ensures that there is at least one user assigned
        self.assertIsNotNone(user_assigned_users)


    def test_modify_card(self):
        """
        Tests the card modification functionality.

        Ensures that a user can access an existing card, make changes to its details,
        and save the modifications. Verifies that the updates are successfully applied to the card.
        """

        # Attempts to create a card before testing modification to ensure a card is available
        try:
            self.test_create_card()
        except Exception:
            print("[INFO] Could not create card")

        driver = self.driver

        # Locates the card element on the board by its CSS class
        card = driver.find_element(By.CLASS_NAME, "card-silhouette")
        # Ensures that the card element is present
        self.assertIsNotNone(card)

        # Clicks the card's title (found using the <h4> tag) to open the card modification form
        card.find_element(By.TAG_NAME, "h4").click()

        # Waits for the "Delete Card" button to appear, indicating that the card edit form loaded
        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "delete-card")))
        except NoSuchElementException as e:
            self.fail(f"Modify card failed: {e}")

        # Locates card form fields and buttons by their respective IDs and CSS classes
        title = driver.find_element(By.ID, "card_title")
        description = driver.find_element(By.ID, "card_description")
        story_points = driver.find_element(By.ID, "story_points")
        expiration_date = driver.find_element(By.ID, "expiration_date")
        completed = driver.find_element(By.ID, "completed")
        assignee = driver.find_element(By.CLASS_NAME, "assignees").find_elements(By.CLASS_NAME, "input-field")[0]
        confirm_card = driver.find_element(By.ID, "confirm-card")

        #
        # Enters new dummy title, description, story_points, expiration_date data
        #
        title.clear()
        title.send_keys(self.dummy_card_title)

        description.clear()
        description.send_keys(self.dummy_card_description)

        story_points.clear()
        story_points.send_keys(self.dummy_card_story_points)

        expiration_date.clear()
        expiration_date.send_keys(self.dummy_card_date_expire)

        # Clicks the checkbox to mark the card as completed
        completed.click()

        # Selects an assignee from the dropdown by clicking the appropriate input field
        assignee.click()

        # Clicks the "Confirm" button to save the changes to the card
        confirm_card.click()

        sleep(2)

        # Waits for the card element to reappear in the column, indicating successful modification
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-silhouette")))
        except NoSuchElementException as e:
            # The test fails if the card element does not reappear
            self.fail(f"Modify card failed: {e}")

        # Locates the assignee's image within the card to confirm the assignee selection applied successfully
        result = result.find_element(By.CLASS_NAME, "card-assignees").find_element(By.TAG_NAME, "img")

        # Verifies that the assignee's image is present, confirming the modification was successful
        self.assertIsNotNone(result)


    def test_delete_card(self):
        """
        Tests the card deletion functionality.

        Ensures that a user can access an existing card, initiate the delete process,
        confirm the deletion, and verifies that the card is removed from the board.
        """

        # Attempts to create a card before testing deletion to ensure a card is available
        try:
            self.test_create_card()
        except Exception:
            print("[INFO] Could not create card")

        driver = self.driver

        # Locates the card element on the board by its CSS class
        card = driver.find_element(By.CLASS_NAME, "card-silhouette")
        # Ensures that the card element is present
        self.assertIsNotNone(card)

        # Clicks the card's title (found using the <h4> tag) to open the card details
        card.find_element(By.TAG_NAME, "h4").click()

        # Waits for the "Delete Card" button to appear, indicating that the card detail view loaded
        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "delete-card")))
        except NoSuchElementException as e:
            self.fail(f"Delete card failed: {e}")

        # Locates and clicks the "Delete Card" button to initiate the deletion process
        delete_card = driver.find_element(By.ID, "delete-card")
        delete_card.click()

        # Waits for the warning advisory dialog to appear, confirming the delete action
        try:
            result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "warning-advisory")))
        except NoSuchElementException as e:
            self.fail(f"Delete card failed: {e}")

        # Locates and clicks the "Confirm" button to finalize the deletion of the card
        confirm_delete = driver.find_element(By.ID, "confirm-dangerous-action")
        confirm_delete.click()

        sleep(2)

        # Verifies that the card element is no longer found, confirming successful deletion
        self.assertRaises(NoSuchElementException, lambda: driver.find_element(By.CLASS_NAME, "card-silhouette"))


    def test_modify_column(self):
        """
        Tests the column modification functionality.

        Ensures that a user can access an existing column, update its title and description,
        save the changes, and verifies that the updates are successfully applied.
        """

        # Attempts to create a column before testing modification to ensure a column is available
        try:
            self.test_create_column()
        except Exception:
            print("[INFO] Could not create column")

        driver = self.driver

        # Locates the column element on the board by its CSS class
        column = driver.find_element(By.CLASS_NAME, "column-silhouette")
        # Ensures that the column element is present
        self.assertIsNotNone(column)

        # Clicks the column's title (found using the <h2> tag) to open the column modification form
        column.find_element(By.TAG_NAME, "h2").click()

        # Waits for the column modal panel to appear, indicating that the column edit form loaded
        try:
            result = self.wait.until(EC.visibility_of_element_located((By.ID, "column-modal-panel")))
        except NoSuchElementException as e:
            self.fail(f"Modify column failed: {e}")

        # Locates the column title, description fields, and the confirm button within the modal
        column_description = result.find_element(By.ID, "column_description")
        column_title = result.find_element(By.ID, "column_title")
        confirm_column = result.find_element(By.ID, "confirm-column")

        # Clears the existing text in the title field and enters new dummy title data
        column_title.clear()
        column_title.send_keys(self.dummy_column_title)

        # Clears the existing text in the description field and enters new dummy description data
        column_description.clear()
        column_description.send_keys(self.dummy_column_description)

        # Clicks the "Confirm" button to save the changes to the column
        confirm_column.click()

        sleep(1)

        # Waits for the service message to appear, confirming the modification was successful
        try:
            result = self.wait.until(EC.visibility_of_element_located((By.ID, "service-message")))
        except NoSuchElementException as e:
            self.fail(f"Modify column failed: {e}")


    def test_delete_column(self):
        """
        Tests the column deletion functionality.

        Ensures that a user can access an existing column, initiate the delete process,
        confirm the deletion, and verifies that the column is removed from the board.
        """

        # Attempts to create a column before testing deletion to ensure a column is available
        try:
            self.test_create_column()
        except Exception:
            print("[INFO] Could not create column")

        driver = self.driver

        # Locates the column element on the board by its CSS class
        column = driver.find_element(By.CLASS_NAME, "column-silhouette")
        # Ensures that the column element is present
        self.assertIsNotNone(column)

        # Moves the cursor over the column element to reveal the delete button
        actions = ActionChains(driver)
        actions.move_to_element(column).perform()

        # Waits for the "Delete" button to appear, indicating that it is visible for interaction
        try:
            result = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "deleting-button")))
        except NoSuchElementException as e:
            self.fail(f"Delete column failed: {e}")

        # Clicks the delete button to initiate the column deletion process
        result.click()

        # Waits for the confirmation dialog to appear, allowing the deletion action to be confirmed
        try:
            result = self.wait.until(EC.presence_of_element_located((By.ID, "confirm-dangerous-action")))
        except NoSuchElementException as e:
            self.fail(f"Delete column failed: {e}")

        # Clicks the confirm button to finalize the deletion of the column
        result.click()

        sleep(1)

        # Verifies that the column element is no longer found, confirming successful deletion
        self.assertRaises(NoSuchElementException, lambda: driver.find_element(By.CLASS_NAME, "column-silhouette"))


    def test_move_card(self):
        """
        Tests the card movement functionality within a column.

        Ensures that a user can access an existing card, drag it to a new position within the column,
        and verifies that the card is successfully moved to the new location.
        """
        driver = self.driver

        # Attempts to create a card before testing movement to ensure cards are available for interaction
        try:
            self.test_create_card()

            # Locates the "Add Card" button and ensures it is present
            add_card = driver.find_element(By.ID, "add-card")
            self.assertIsNotNone(add_card)

            # Clicks the "Add Card" button to open the card creation form
            add_card.click()

            # Waits for the form title to confirm that the card creation form loaded
            try:
                result = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
            except NoSuchElementException as e:
                self.fail(f"Create card failed: {e}")

            # Locates the card creation form fields and the "Create" button
            card_title = driver.find_element(By.ID, "card_title")
            card_description = driver.find_element(By.ID, "card_description")
            card_column = driver.find_element(By.ID, "column")
            card_date = driver.find_element(By.ID, "expiration_date")
            card_story_points = driver.find_element(By.ID, "story_points")
            create_button = driver.find_element(By.ID, "create")

            # Fills in the card title and description fields with sample data
            card_title.send_keys("ToBeFirst")
            card_description.send_keys(self.dummy_card_description)

            # Selects the appropriate column for the card using a dummy column index
            select = Select(card_column)
            select.select_by_index(self.dummy_card_column)

            # Enters the dummy expiration date and story points into the respective fields
            card_date.send_keys(self.dummy_card_date_expire)
            card_story_points.send_keys(self.dummy_card_story_points)

            # Clicks the "Create" button to submit the new card form
            create_button.click()

            # Waits for the second card to appear, confirming successful creation of two cards
            try:
                result = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card-silhouette + .card-silhouette")))
            except NoSuchElementException as e:
                self.fail(f"Create card failed: {e}")

            # Verifies that we are still on the board page
            self.assertEqual("Kanboard - " + self.dummy_board, driver.title)

        except Exception:
            print("[INFO] Could not create card")

        # Locates the two card elements for interaction
        card, card2 = driver.find_elements(By.CLASS_NAME, "card-silhouette")

        sleep(1)

        # Initiates an action chain to drag the first card to a new position in the column
        action = ActionBuilder(driver)
        action.pointer_action.move_to(card).click_and_hold(card).move_to_location(card.location['x'], card.location['y'] + 450).release()
        action.perform()

        sleep(1)

        # Waits for the drag-and-drop placeholder to appear, indicating that the card has moved
        try:
            result = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".card-silhouette + .card-silhouette + #dnd-placeholder")))
        except NoSuchElementException as e:
            self.fail(f"Drag and drop failed: {e}")


    def test_move_column(self):
        """
        Tests the column movement functionality on the board.

        Ensures that a user can access an existing column, drag it to a new position on the board,
        and verifies that the column is successfully moved to the new location.
        """
        driver = self.driver

        # Attempts to create a column before testing movement to ensure columns are available for interaction
        try:
            self.test_create_column()

            # Locates the "Add Column" button on the board and ensures it is present
            add_column = driver.find_element(By.ID, "add-column")
            self.assertIsNotNone(add_column)

            # Clicks the "Add Column" button to open the column creation form
            add_column.click()

            # Waits for the form title to confirm that the column creation form loaded
            try:
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-title")))
            except NoSuchElementException as e:
                self.fail(f"Create column failed: {e}")

            # Locates the column creation form fields and the "Create" button
            column_title = driver.find_element(By.ID, "column_title")
            column_description = driver.find_element(By.ID, "column_description")
            create_button = driver.find_element(By.ID, "create")

            # Fills in the column title and description fields with sample data
            column_title.send_keys("ToBeFirst")
            column_description.send_keys(self.dummy_column_description)

            # Clicks the "Create" button to submit the new column form
            create_button.click()

            # Waits for the second column to appear, confirming successful creation of two columns
            try:
                result = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modable + .modable")))
            except NoSuchElementException as e:
                self.fail(f"Create column failed: {e}")

        except Exception:
            print("[INFO] Could not create column")

        # Locates the two column elements for interaction
        column, column2 = driver.find_elements(By.CLASS_NAME, "column-silhouette")
        column = column.find_element(By.TAG_NAME, "p")

        sleep(1)

        # Initiates an action chain to drag the first column to a new position on the board
        actions = ActionChains(driver)
        actions.drag_and_drop_by_offset(column, 500, 0).perform()

        sleep(1)

        # Waits for the drag-and-drop placeholder to appear, indicating that the column has moved
        try:
            result = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modable + .modable + #dnd-placeholder")))
        except NoSuchElementException as e:
            self.fail(f"Move column failed: {e}")



if __name__ == "__main__":
    unittest.main()
