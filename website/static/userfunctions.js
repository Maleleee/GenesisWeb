let sidebarOpen = false;
const sidebar = document.querySelector('.sidebar'); // Use class if no ID is available

// Function to open the sidebar
function openSidebar() {
  if (!sidebarOpen) {
    sidebar.classList.add('sidebar-responsive'); // Add responsive class
    sidebarOpen = true;
  }
}

// Function to close the sidebar
function closeSidebar() {
  if (sidebarOpen) {
    sidebar.classList.remove('sidebar-responsive'); // Remove responsive class
    sidebarOpen = false;
  }
}

// Function to close Withdraw modal
function closeWithdraw() {
  document.getElementById("withdrawModal").style.display = "none";
}

// Function to close Deposit modal
function closeDeposit() {
  document.getElementById("depositModal").style.display = "none";
}

// Function to close Transactions modal
function closeTransactions() {
  document.getElementById("transactionsModal").style.display = "none";
}

// Function to open Withdraw modal
function openWithdraw() {
  document.getElementById("withdrawModal").style.display = "flex";
}

// Function to open Deposit modal
function openDeposit() {
  document.getElementById("depositModal").style.display = "flex";
}

// Function to open Transactions modal
function openTransactions() {
  document.getElementById("transactionsModal").style.display = "flex";
}

// Close modal when clicking outside of it
window.onclick = function(event) {
  const withdrawModal = document.getElementById("withdrawModal");
  const depositModal = document.getElementById("depositModal");
  const transactionsModal = document.getElementById("transactionsModal");
  
  if (event.target === withdrawModal) {
      closeWithdraw();
  }
  if (event.target === depositModal) {
      closeDeposit();
  }
  if (event.target === transactionsModal) {
      closeTransactions();
  }
}
