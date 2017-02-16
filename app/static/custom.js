// Menu
jQuery(document).ready(function($){
    //open popup
    $('.cd-popup-trigger').on('click', function(event){
        event.preventDefault();
        $('.cd-popup').addClass('is-visible');
    });

    //close popup
    $('.cd-popup').on('click', function(event){
        if( $(event.target).is('.cd-popup-close') || $(event.target).is('.cd-popup') ) {
            event.preventDefault();
            $(this).removeClass('is-visible');
        }
        if( $(event.target).is('.cd-popup-cancel') || $(event.target).is('.cd-popup') ) {
            event.preventDefault();
            $(this).removeClass('is-visible');
        }
    });
    //close popup when clicking the esc keyboard button
    $(document).keyup(function(event){
        if(event.which=='27'){
            $('.cd-popup').removeClass('is-visible');
        }
    });
});

// Remove focus from navbar menu button after click/tap
$(document).ready(function () {
    $(".navbar-toggle").click(function(event) {
        // Removes focus of the button.
        $(this).blur();
    });
});


// Autocomplete quicknav search form
$(document).ready(function() {
    var aTags = "/autocomplete";
    $( "#tags" ).autocomplete({
        source: aTags
    });
});