function validationResult(result, message) {
    return result || (displayMessage({status: 500, message: message}) || false);
}

function validateUsername(username) {
    const re = /^[a-zA-Z0-9_]+$/;
    return validationResult(re.test(username), "Username must contain only letters, numbers and underscores");
}

function validateEmail(email) {
    const re = /^[a-zA-Z0-9_]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+$/;
    return validationResult(re.test(email), "Invalid email address");
}

function validatePassword(password) {
    const re = /^[a-zA-Z0-9_%$&,@!?]{8,}$/;
    return validationResult(re.test(password), "Password must contain at least 8 characters");
}

function validatePasswordMatch(password) {
    return validationResult(password === document.querySelector('input[name="password"]').value, "Passwords do not match");
}

function validateName(name) {
    const re = /^[a-zA-Z ]+$/;
    return validationResult(name.length >= 2 && re.test(name), "Name must contain only letters and be at least 2 characters long");
}

function validateSurname(surname) {
    const re = /^[a-zA-Z ]+$/;
    return validationResult(surname.length >= 2 && re.test(surname), "Surname must contain only letters and be at least 2 characters long");
}

function validateImage(image) {
    const re = /^image\/(jpeg|png|jpg)$/;
    console.log(re.test(image.type))
    return validationResult(re.test(image.type), "Invalid image format");
}

function validateBoardTitle(title) {
    const re = /^[a-zA-Z0-9 ]{1,16}$/;
    return validationResult(re.test(title), "Board title must contain only letters and numbers and be at most 16 characters long");
}

function validateBoardDescription(description) {
    const re = /^[a-zA-Z0-9 .,;:!?-_()\n]{0,256}$/;
    return validationResult(re.test(description), "Board description must contain only letters and numbers and be at most 256 characters long");
}

function validateColumnTitle(title) {
    const re = /^[a-zA-Z0-9 ]{1,20}$/;
    return validationResult(re.test(title), "Column title must contain only letters and numbers and be at most 20 characters long");
}

function validateColumnDescription(description) {
    const re = /^[a-zA-Z0-9 .,;:!?-_()\n]{1,256}$/;
    return validationResult(re.test(description), "Column description must contain only letters and numbers and be at most 256 characters long");
}

function validateCardTitle(title) {
    const re = /^[a-zA-Z0-9 ]{1,20}$/;
    return validationResult(re.test(title), "Card title must contain only letters and numbers and be at most 20 characters long");
}

function validateCardDescription(description) {
    const re = /^[a-zA-Z0-9 .,;:!?\-_()\n]{0,256}$/;
    return validationResult(re.test(description), "Card description must contain only letters and numbers and be at most 256 characters long");
}


const validators = [
    {validator: validateUsername, label: "username"},
    {validator: validateEmail, label: "email"},
    {validator: validatePassword, label: "password"},
    {validator: validatePasswordMatch, label: "password"},
    {validator: validateName, label: "name"},
    {validator: validateSurname, label: "surname"},
    {validator: validateImage, label: "image"},
    {validator: validateBoardTitle, label: "board_title"},
    {validator: validateBoardDescription, label: "board_description"},
    {validator: validateColumnTitle, label: "column_title"},
    {validator: validateColumnDescription, label: "column_description"},
    {validator: validateCardTitle, label: "card_title"},
    {validator: validateCardDescription, label: "card_description"},
]
