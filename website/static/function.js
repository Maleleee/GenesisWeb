const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');
const signUpForm = document.querySelector('.sign-up form');

// Check session storage for active state
if (sessionStorage.getItem('activeForm') === 'register') {
    container.classList.add("active");
} else {
    container.classList.remove("active");
}

// Add event listeners to the buttons
registerBtn.addEventListener('click', (event) => {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Add active class to the container only if there are no error messages
    if (!signUpForm.querySelector('.error')) {
        container.classList.add("active");
        sessionStorage.setItem('activeForm', 'register'); // Save state
    }
});

loginBtn.addEventListener('click', () => {
    // Remove active class from the container
    container.classList.remove("active");
    sessionStorage.setItem('activeForm', 'login'); // Save state
});
