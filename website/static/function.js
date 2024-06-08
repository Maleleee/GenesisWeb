const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');
const signUpForm = document.querySelector('.sign-up form');

// Add event listeners to the buttons
registerBtn.addEventListener('click', (event) => {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Add active class to the container only if there are no error messages
    if (!signUpForm.querySelector('.error')) {
        container.classList.add("active");
    }
});

loginBtn.addEventListener('click', () => {
    // Remove active class from the container
    container.classList.remove("active");
});
