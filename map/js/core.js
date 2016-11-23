      var flickrapikey = "b522feb6513d0401a1e27cc438739776";
      var map;
      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          center: {lat: 52.520007, lng: 13.404954},
          zoom: 13
        });
  //thanks to https://www.doogal.co.uk/FullScreen.php
  map.controls[google.maps.ControlPosition.TOP_RIGHT].push(
   FullScreenControl(map));

  function Category(name) {
    var self = this;
    self.name = name
    self.visible = ko.observable(true);
    self.toggle = function() {
      self.visible(!self.visible());
      vm.filtered =true;
      vm.UpdateView();
    };
  };
  function MapMarker(name, category, lat, lng) {
    var self = this;
    self.name = name;
    self.category = category;
    self.lat = lat;
    self.lng = lng;
    self.marker = new google.maps.Marker({
      position: {lat: self.lat, lng: self.lng},
      map: map,
      title: self.name
    });
    self.show = ko.observable(true);
    self.showAlone = function() {
      if (vm.filtered == false) {
        vm.ClearView(); 
        vm.filtered = true; 
      }
      self.marker.setMap(map);
      self.show(true);
      self.marker.setAnimation(google.maps.Animation.BOUNCE);
    }
    self.details = function () {
      //get images from flickr and generate the info window.
      $.getJSON("http://api.flickr.com/services/feeds/photos_public.gne?jsoncallback=?",
      {
        tags: self.name,
        tagmode: "any",
        format: "json"
      },
      function(data) {
        ret = '<div class="mapPopUp">'
        ret += '<h2>' + self.name + '</h2>'
        $.each(data.items, function(i,item){
          ret += '<img class="img-responsive" src="' + item.media.m + '">'
          if (i > 2) {
            return false;
          }
        });
        ret += "</div>"
        if (vm.infowindow){
          vm.infowindow.close();
        }
        vm.infowindow = new google.maps.InfoWindow({
          content: ret,
          maxWidth: 200
        });
        vm.infowindow.open(map, self.marker)
      }).fail(function() { alert('flickr wont provide any images right now :/'); });
    }
    self.marker.addListener('click', self.details);
  }

          // Overall viewmodel for this screen, along with initial data
          function MarkerViewModel() {
            var self = this;   
            self.filtered = false;
            // Initial data
            self.categories = [
              new Category("Type A"),
              new Category("Type B"), 
              new Category("Type C")
              ];
            self.marker = [
              new MapMarker("Alex", self.categories[1], 52.521649, 13.411313),
              new MapMarker("Rotes Rathaus", self.categories[0], 52.518450, 13.408309),
              new MapMarker("Reichstag", self.categories[2], 52.518437, 13.375329),
              new MapMarker("Rosa-Luxemburg-Platz", self.categories[1], 52.528646, 13.410090),
              new MapMarker("Checkpoint Charly", self.categories[0], 52.507337, 13.390199)
              ];
            function setMapOnAll(map,on) {
                for (var i = 0; i < self.marker.length; i++) {
                  self.marker[i].marker.setMap(map);
                  self.marker[i].category.visible(on);
                }
              }
            self.FilterList = ko.computed(function() {
                return ko.utils.arrayFilter(self.marker, function(marker) {
                  return marker.category.visible;
                });
              });
            self.UpdateView = function () {
                for (var i = 0; i < self.marker.length; i++) {
                  if (self.marker[i].category.visible()) {
                    self.marker[i].marker.setMap(map);
                  }
                  else
                  {
                    self.marker[i].marker.setMap(null);
                  }
                }
              }
            self.ClearView = function() {
                self.filtered = true;
                setMapOnAll(null, false);
              }
            self.FullView = function() {
                self.filtered = false;
                setMapOnAll(map, true);
              }


            }
            vm = new MarkerViewModel()
            ko.applyBindings(vm);
          }
          function googleError() {
            window.alert("Failed to load Map API, pls reload.");
          }
          function knockoutError() {
            window.alert("Failed to load  knockout, pls reload.");
          }