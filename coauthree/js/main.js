function start( e ){
    var scene = new THREE.Scene();

    // setup Camera
    var camera = new THREE.PerspectiveCamera(12,
                                         window.innerWidth / window.innerHeight,
                                         20000);
    camera.position.z = 1400;
    camera.position.y = 0;
    camera.lookAt(scene.width/2, scene.height/2);

    // light
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

    /* rotating = new THREE.Object3D();
    scene.add(rotating);

    lookupCanvas = document.createElement( 'canvas' );
    lookupCanvas.width = 256;
    lookupCanvas.height = 1;

    */

    // renderer
    var renderer = new THREE.WebGLRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.autoClear = false;
    renderer.sortObjects = false;
    glContainer.appendChild( renderer.domElement );

    // add sphere
    scene.add(camera);
    var geometry = new THREE.SphereGeometry(100, 40, 40);
    var material = new THREE.MeshPhongMaterial();
    var earthMesh = new THREE.Mesh(geometry, material);
    scene.add(earthMesh);
    renderer.render( scene, camera );
};
