
require(["vendor/three.min", "util"], function(THREE, util){
    console.log("coauthree has been run !!");
    // var THREE = require("/js/three.min.js");
    var cityinfo = "/cities_lat_lon.json";
    var mapIndexedImage = new Image();
    var mapOutlineImage = new Image();

    console.log("this is main !!");
    util.test("world!!");
    util.init_scene();
});
