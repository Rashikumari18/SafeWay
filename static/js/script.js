(function(){
  const areaInputs = [document.getElementById("areaA"), document.getElementById("areaB")].filter(Boolean);
  document.querySelectorAll(".quick button, .saved-chip").forEach(btn=>{
    btn.addEventListener("click",()=>{
      const area=btn.dataset.area;
      if(!areaInputs[0].value) areaInputs[0].value=area;
      else areaInputs[1].value=area;
    });
  });

  if(document.getElementById("map") && window.L){
    const map=L.map("map",{zoomControl:true}).setView([22.5726,88.3639],12);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"© OpenStreetMap contributors"}).addTo(map);
    const points=[
      ["Central Market",22.5726,88.3639],
      ["Lake Road",22.5448,88.3426],
      ["College Road",22.5800,88.4000],
      ["Station Road",22.5697,88.3697]
    ];
    const areaA=document.getElementById("areaA"), areaB=document.getElementById("areaB");
    points.forEach((p)=>{
      const marker=L.marker([p[1],p[2]]).addTo(map);
      marker.bindPopup(`<b>${p[0]}</b><br><button class="map-pick" data-area="${p[0]}">Use for route</button>`);
      marker.on("popupopen",()=>{
        const pick=document.querySelector(`.map-pick[data-area="${p[0]}"]`);
        if(pick) pick.onclick=()=>{ if(!areaA.value) areaA.value=p[0]; else areaB.value=p[0]; map.closePopup(); };
      });
    });
    const locate=document.getElementById("locateBtn"), status=document.getElementById("locationStatus");
    if(locate){
      locate.addEventListener("click",()=>{
        if(!navigator.geolocation){status.textContent="Browser location is not available.";return;}
        status.textContent="Requesting location permission…";
        navigator.geolocation.getCurrentPosition(pos=>{
          map.setView([pos.coords.latitude,pos.coords.longitude],15);
          L.circleMarker([pos.coords.latitude,pos.coords.longitude],{radius:7}).addTo(map).bindPopup("Your current browser location").openPopup();
          status.textContent="Centered on your browser location. It is not stored by SafeWay.";
        },()=>{status.textContent="Location permission was not granted.";},{enableHighAccuracy:false,timeout:8000});
      });
    }
  }
})();
