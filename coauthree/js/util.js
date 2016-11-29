define(["Three.min"], function(THREE){

    var test = function(world){
        console.log("Hello !!" + world);
    };

    var init_scene = function(){
 	    var scene = new THREE.Scene();
        var camera = new THREE.PerspectiveCamera(12,
			window.innerWidth / window.innerHeight,
            20000);
    };

    return {
        test: test,
	    init_scene: init_scene
    };
});
