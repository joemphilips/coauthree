define(["vendor/three.min", "jquery-1.7.1.min"], function(THREE, jquery){
    function test(world){
        console.log("HELLO!!" + world)
    }

    function init_scene(){
        var scene = new THREE.Scene();

        scene = _build_scene(scene);
        camera = _build_camera(scene);

        renderer = _build_renderer();

        renderer.render( scene, camera );
    };

    function _build_scene(scene){
        scene = _add_light(scene);
        scene = _add_earth(scene);
        return scene;
    };

    function _build_renderer() {
        var renderer = new THREE.WebGLRenderer();
        renderer.setSize( window.innerWidth, window.innerHeight );
        renderer.autoClear = false;
        renderer.sortObjects = false;
        $("#dataviz").append( renderer.domElement );

        return renderer;
    }

    function _add_light(scene){
        scene.add( new THREE.AmbientLight( 0x505050 ) );

        var light1 = new THREE.SpotLight( 0xeeeeee, 3 );
        light1.position.x = 730;
        light1.position.y = 520;
        light1.position.z = 626;
        light1.castShadow = true;
        scene.add( light1 );

        light2 = new THREE.PointLight( 0x222222, 14.8 );
        light2.position.x = -640;
        light2.position.y = -500;
        light2.position.z = -1000;
        scene.add( light2 );

        return scene;
    };

    function _build_camera(scene){
        var camera = new THREE.PerspectiveCamera(12,
                window.innerWidth / window.innerHeight,
                20000);
        camera.position.z = 1400;
        camera.position.y = 0;
        camera.lookAt(scene.width/2, scene.height/2);

        return camera;
    };

    function _add_earth(scene){
        var geometry = new THREE.SphereGeometry(100, 40, 40);
        var material = new THREE.MeshPhongMaterial();
        var earthMesh = new THREE.Mesh(geometry, material);
        scene.add(earthMesh);

        return scene;
    };

    return {init_scene: init_scene, test: test};
});


