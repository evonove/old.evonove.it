// var $cjq for better adaptation and work with other libraries
var $cjq = jQuery.noConflict();

$cjq(document).ready(function(){
// isotope start

	if ($cjq('#home_responsive').length>0) {
		$cjq('#home_responsive').isotope({
			itemSelector: '.hp-wrapper',
			layoutMode: 'masonry'
		});
	}
	if ($cjq('#clients').length>0) {
		$cjq('#clients').isotope({
			itemSelector: '.hp-wrapper',
			layoutMode: 'masonry'
		});
	}
	if ($cjq('#portfolio').length>0) {
		$cjq('#portfolio').isotope({
			itemSelector: '.hp-wrapper',
			layoutMode: 'masonry'
		});
	}
	if ($cjq('#gallery-main').length>0) {
		$cjq('#gallery-main').isotope({
			itemSelector: '.hp-wrapper',
			layoutMode: 'masonry'
		});
	}
	if ($cjq('#gallery').length>0) {
		$cjq('#gallery').isotope({
			itemSelector: '.hp-wrapper',
			layoutMode: 'masonry'
		});
	}

// isotope end

	$cjq('.dropdown-toggle').dropdown();
	
	$cjq('.carousel').carousel();
	
    $cjq(".dropdown").hover(
        function () {
            $cjq(this).addClass("open");
        },
        function () {
            $cjq(this).removeClass("open");
        }
        );
	
	$cjq("<select />").appendTo(".buttons-container");
    $cjq(".buttons-container select").addClass('nav-select');
	
    $cjq(".nav-collapse a").each(function() {
        var el = $cjq(this);
		
        if (el.parent().hasClass("active")){
            $cjq("<option />", {
                "selected": "selected",
                "value"   : el.attr("href"),
                "text"    : el.html().replace(/<i>.*<\/i>/gi,'')
            }).appendTo(".buttons-container select");
        } else {
            $cjq("<option />", {
                "value"   : el.attr("href"),
                "text"    : el.html().replace(/<i>.*<\/i>/gi,'')
            }).appendTo(".buttons-container select");
        }
    });
	
    $cjq(".buttons-container select").change(function() {
        window.location = $cjq(this).find("option:selected").val();
    });
	
	$cjq('.accordion').collapse();
    $cjq('.accordion').on('shown', function () {
        var $aGroup = $cjq('.accordion-group');
        $aGroup.find('.accordion-body').not(".in").prev('.accordion-heading').children("a").addClass('collapsed');
			
    })
	
	var $toggleBoxes = $cjq(".toggle-box");
    $toggleBoxes.find('.tbox-heading').children(".collapsed").parent().next(".tbox-inner").css('display', 'none');
	
	/*$cjq("a.thumbnail, a.fancy").fancybox({
        'transitionIn'	:	'elastic',
        'transitionOut'	:	'elastic',
        'speedIn'		:	600, 
        'speedOut'		:	200, 
        'overlayShow'	:	false
    });
	*/
});

$cjq(".toggle-box .tbox-heading a").click(function () {
    if ($cjq(this).hasClass("collapsed")) {
        $cjq(this).parent().next(".tbox-inner").slideDown('fast');
        $cjq(this).removeClass("collapsed");
    } else {
        $cjq(this).parent().next(".tbox-inner").slideUp('fast');
        $cjq(this).addClass("collapsed");
    }
    return false;
});

$cjq('#filters a').click(function(){
    var $this = $cjq(this);
    // don't proceed if already selected
    if ( $this.hasClass('selected') ) {
        return false;
    }
    var $optionSet = $this.parents('.option-set');
    $optionSet.find('.selected').removeClass('selected');
        
    var selector = $this.attr('data-filter');
    $cjq('#portfolio, #gallery').isotope({
        filter: selector
    });
		
    $this.parent.addClass('selected');
    return false;
});
$cjq(function(){
      
    var $container = $cjq('#container');

    $container.isotope({
        itemSelector : '.element'
    });
      
      
    var $optionSets = $cjq('#options .option-set'),
    $optionLinks = $optionSets.find('a');

    $optionLinks.click(function(){
        var $this = $cjq(this);
        // don't proceed if already selected
        if ( $this.hasClass('selected') ) {
            return false;
        }
        var $optionSet = $this.parents('.option-set');
        $optionSet.find('.selected').removeClass('selected');
        $this.addClass('selected');
  
        // make option object dynamically, i.e. { filter: '.my-filter-class' }
        var options = {},
        key = $optionSet.attr('data-option-key'),
        value = $this.attr('data-option-value');
        // parse 'false' as false boolean
        value = value === 'false' ? false : value;
        options[ key ] = value;
        if ( key === 'layoutMode' && typeof changeLayoutMode === 'function' ) {
            // changes in layout modes need extra logic
            changeLayoutMode( $this, options )
        } else {
            // otherwise, apply new options
            $container.isotope( options );
        }
        
        return false;
    });

      
});

$cjq(document).ready(function(){
	
	if ($cjq("#carousel").length || $cjq("#slider").length){
		$cjq('#carousel').flexslider({
			animation: "slide",
			controlNav: false,
			animationLoop: true,
			slideshow: false,
			itemWidth: 80,
			itemMargin: 5,
			asNavFor: '#slider'
		});
	   
		$cjq('#slider').flexslider({
			animation: "slide",
			controlNav: false,
			animationLoop: false,
			slideshow: false,
			sync: "#carousel"
		});
	} else {
		if ($cjq(".flexslider").length){
			$cjq(".flexslider").flexslider({
				animation: "slide"
			});
		}
	}
    // $cjq(".fancybox").fancybox();

	// TODO: update to Twitter API 1.1
	/* twitter feed
	$cjq.ajax({
		url: 'https://api.twitter.com/1/statuses/user_timeline.json/',
		type: 'GET',
		dataType: 'jsonp',
		data: {
			screen_name: 'evonove',
			include_rts: true,
			count: 5,
			include_entities: true
		},
		success: function(data, textStatus, xhr) {
			var html = '';
			for (var i = 0; i < data.length; i++) {
				html = html +'<li class="latest-tweet"><p>' + data[i].text + '</p></li>';
			}
			$cjq(".tweets-slide ul").append($cjq(html));
			var height_li = 30;
			$cjq(".tweets-slide ul li").each(function() {
				$cjq(this).css('height', '');
				if ($cjq(this).outerHeight(true) > height_li) height_li = $cjq(this).outerHeight(true);
			});
			$cjq(".tweets-slide ul li").each(function() {
				var margin = Math.floor((height_li-$cjq(this).outerHeight(true))/2);
				$cjq(this).css('height', height_li);
				$cjq(this).children("p").css('margin-top', margin);
			});
			$cjq('.tweets-slide').flexslider({
				animation: "slide",
				keyboard: false,
				controlNav: false,
				directionNav: true,
				prevText: "Previous",
				nextText: "Next",
				direction: "vertical",
				pauseOnHover: false,
				animationSpeed: 400,
				slideshowSpeed: 3000,
				controlsContainer: "#nav_t"
			});
			$cjq("#nav_t").css('margin-top', Math.floor(((height_li - $cjq("#nav_t").outerHeight(true))/2)));
			$cjq(".follow_img").css('margin-top', Math.floor(((height_li - $cjq(".follow_img").outerHeight(true))/2)));
		}
	});*/

});
$cjq(window).bind('resize', function() {
	if ($cjq(".tweets-slide ul li").length>0) {
		var height_li = 0;
		$cjq(".tweets-slide ul li").each(function() {
			$cjq(this).css('height', '');
			if ($cjq(this).outerHeight(true) > height_li) height_li = $cjq(this).outerHeight(true);
		});
		$cjq(".tweets-slide ul li").each(function() {
			var margin = Math.floor((height_li-$cjq(this).outerHeight(true))/2);
			$cjq(this).css('height', height_li);
			$cjq(this).children("p").css('margin-top', margin);
		});
		$cjq("#nav_t").css('margin-top', Math.floor(((height_li - $cjq("#nav_t").outerHeight(true))/2)+2));
		$cjq(".follow_img").css('margin-top', Math.floor(((height_li - $cjq(".follow_img").outerHeight(true))/2)+1));
	}
});
