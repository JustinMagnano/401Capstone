//Sidebar
let button = document.querySelector('#button');
let sidebar = document.querySelector('.sidebar');

button.onclick = function () {
  sidebar.classList.toggle('active');
};

//Dark/Light mode.
let darkMode = localStorage.getItem('darkMode'); 

const darkModeToggle = document.querySelector('#dark-mode-toggle');
const enableDarkMode = () => {
  document.body.classList.add('darkmode');
  localStorage.setItem('darkMode', 'enabled');
}

const disableDarkMode = () => {
  document.body.classList.remove('darkmode');
  localStorage.setItem('darkMode', null);
}
 
if (darkMode === 'enabled') {
  enableDarkMode();
}

darkModeToggle.addEventListener('click', () => {
  darkMode = localStorage.getItem('darkMode'); 
  
  if (darkMode !== 'enabled') {
    enableDarkMode();
  } else {  
    disableDarkMode(); 
  }


});

setInterval(() => {
  var now = new Date();
  var datetime=now.toLocaleString();
  document.getElementById("datetime").innerHTML = datetime;  
}, 1000);
