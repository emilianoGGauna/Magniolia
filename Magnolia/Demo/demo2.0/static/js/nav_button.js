document.addEventListener('DOMContentLoaded', function() {
    var hamburger = document.querySelector('.hamburger-menu');
    var navButtons = document.querySelector('.nav-buttons');

    // Inicia con el menú de navegación cerrado
    navButtons.style.display = 'none';

    hamburger.addEventListener('click', function() {
        // Alterna la visibilidad de los botones de navegación
        if (navButtons.style.display === 'block') {
            navButtons.style.display = 'none';
        } else {
            navButtons.style.display = 'block';
        }
    });
});
