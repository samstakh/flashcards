document.addEventListener('DOMContentLoaded', function () {
    console.log("Script loaded");

    const addDeckButton = document.getElementById('addDeckButton');
    const cancelAddDeckButton = document.getElementById('cancelAddDeckButton');
    const deckDisplay = document.getElementById('deck-display');
    const addDeckForm = document.getElementById('add-deck-form');

    if (addDeckButton) {
        addDeckButton.addEventListener('click', function () {
            console.log("Add button clicked");
            if (deckDisplay && addDeckForm) {
                deckDisplay.hidden = true;
                addDeckForm.hidden = false;
            }
        });
    }

    if (cancelAddDeckButton) {
        cancelAddDeckButton.addEventListener('click', function () {
            console.log("Cancel clicked");
            if (deckDisplay && addDeckForm) {
                deckDisplay.hidden = false;
                addDeckForm.hidden = true;
            }
        });
    }


    document.querySelectorAll('.card-hover').forEach(card => {
        card.addEventListener('mouseenter', () => {
          const actions = card.querySelector('.card-actions');
          if (actions) actions.style.display = 'flex';
        });
  
        card.addEventListener('mouseleave', () => {
          const actions = card.querySelector('.card-actions');
          if (actions) actions.style.display = 'none';
        });
      });
});
