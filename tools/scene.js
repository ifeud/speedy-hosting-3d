import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

// All geometry, lighting and textures are created locally. No network assets.
(() => {
  const host = document.querySelector('#engine-stage');
  const canvas = document.querySelector('#engine-canvas');
  if (!host || !canvas) return;
  function useFallback(){
    host.classList.add('render-fallback');host.classList.remove('scene-ready');
    canvas.hidden=true;canvas.removeAttribute('tabindex');canvas.setAttribute('aria-hidden','true');
    const tools=host.parentElement.querySelector('.engine-tools');
    if(tools){const caption=tools.querySelector('span');if(caption)caption.textContent='Hardware illustration';}
    const reset=document.querySelector('#reset-engine');if(reset)reset.disabled=true;
  }
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({canvas, alpha:true, antialias:true, powerPreference:'low-power'});
  } catch (_) {
    useFallback();
    return;
  }
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 80);
  camera.position.set(8.3, 5.4, 12.3);
  camera.lookAt(0, .05, 0);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.65));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = .97;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const env = pmrem.fromScene(room, .05);
  scene.environment = env.texture;
  scene.environmentIntensity = 1.05;
  room.dispose(); pmrem.dispose();

  const world = new THREE.Group();
  scene.add(world);
  world.rotation.y = -.22;
  const metal = new THREE.MeshPhysicalMaterial({color:0x111518, metalness:.67, roughness:.36, clearcoat:.2, clearcoatRoughness:.3});
  const edge = new THREE.MeshStandardMaterial({color:0x20272b, metalness:.75, roughness:.26});
  const dark = new THREE.MeshStandardMaterial({color:0x07090c, metalness:.35, roughness:.5});
  const orange = new THREE.MeshStandardMaterial({color:0xff6c30, metalness:.15, roughness:.32, emissive:0xff5216, emissiveIntensity:.46});
  const screw = new THREE.MeshStandardMaterial({color:0x7a8288, metalness:.9, roughness:.2});
  const concrete = new THREE.MeshStandardMaterial({color:0x111719, roughness:.86, metalness:.03});
  const round = (w,h,d,r=.1) => new RoundedBoxGeometry(w,h,d,4,r);
  const mesh = (geometry, material, x,y,z, parent=world) => {
    const m = new THREE.Mesh(geometry,material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;
  };
  const base = mesh(round(5.9,.38,4.15,.08),concrete,0,-2.06,0);
  // Three staggered, precision-machined engine modules.
  const modules=[];
  for(let layer=0;layer<3;layer++) {
    const y=-1.29+layer*1.31;
    const x=(layer-1)*.43;
    const module=new THREE.Group();module.position.set(x,y,0);world.add(module);modules.push(module);
    mesh(round(4.7,1.1,3.35,.1),metal,0,0,0,module);
    mesh(round(4.49,.035,3.15,.012),edge,0,.563,0,module);
    // Recessed front fascia and warm vents.
    mesh(round(4.49,.84,.065,.035),dark,0,-.015,1.677,module);
    for(let i=0;i<16;i++) {
      const vx=-1.42+i*.188;
      mesh(round(.075,.49,.024,.012),orange,vx,.02,1.722,module);
      mesh(new THREE.BoxGeometry(.07,.51,.023),edge,vx-.064,.02,1.719,module);
    }
    // Small hardware details, deliberately not fake UI readouts.
    for(const sx of [-2.09,2.09])for(const sy of [-.34,.34]) {
      const bolt=mesh(new THREE.CylinderGeometry(.027,.027,.023,12),screw,sx,sy,1.728,module);bolt.rotation.x=Math.PI/2;
      mesh(new THREE.BoxGeometry(.028,.006,.002),dark,sx,sy,1.745,module);
    }
    for(let i=0;i<7;i++)mesh(new THREE.BoxGeometry(.018,.64,.07),dark,2.36,-.005,-.95+i*.3,module);
    // A restrained etched speed mark on the front corner.
    const plate=mesh(round(.43,.22,.018,.025),edge,1.82,.04,1.731,module);
    for(let i=0;i<3;i++) {
      const slash=mesh(new THREE.BoxGeometry(.025,.1,.006),orange,1.75+i*.067,.04,1.746,module);slash.rotation.z=-.5;
    }
  }
  // Batch the static sculpture by material for fast rendering on modest GPUs.
  world.updateMatrixWorld(true);
  const inverseWorld=new THREE.Matrix4().copy(world.matrixWorld).invert();
  const batches=new Map();
  world.traverse(object=>{
    if(!object.isMesh)return;
    let geometry=object.geometry.clone();
    if(geometry.index){const raw=geometry.toNonIndexed();geometry.dispose();geometry=raw;}
    geometry.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inverseWorld,object.matrixWorld));
    if(!batches.has(object.material))batches.set(object.material,[]);
    batches.get(object.material).push(geometry);
  });
  world.traverse(object=>{if(object.isMesh)object.geometry.dispose();});
  world.clear();
  for(const [material,geometries] of batches){
    const combined=mergeGeometries(geometries,false);
    const object=new THREE.Mesh(combined,material);object.castShadow=true;object.receiveShadow=true;world.add(object);
    geometries.forEach(geometry=>geometry.dispose());
  }
  const halo = new THREE.Mesh(new THREE.TorusGeometry(3.48,.009,8,160),new THREE.MeshBasicMaterial({color:0x68584c,transparent:true,opacity:.38}));
  halo.position.set(0,.18,-2.75);halo.rotation.y=.13;scene.add(halo);
  const ambient = new THREE.HemisphereLight(0xced8e1,0x101318,.85);scene.add(ambient);
  const key = new THREE.DirectionalLight(0xffe3c7,3.3);key.position.set(5,9,8);key.castShadow=true;
  key.shadow.mapSize.set(1024,1024);key.shadow.camera.left=-8;key.shadow.camera.right=8;key.shadow.camera.top=7;key.shadow.camera.bottom=-7;key.shadow.bias=-.001;key.shadow.normalBias=.05;scene.add(key);
  const rim = new THREE.DirectionalLight(0xff773e,2.9);rim.position.set(-7,3,-4);scene.add(rim);
  const fill = new THREE.DirectionalLight(0xc4daef,1.5);fill.position.set(4,2,-3);scene.add(fill);
  // Soft contact shadow, rendered procedurally on a transparent plane.
  const shadowCanvas=document.createElement('canvas');shadowCanvas.width=shadowCanvas.height=128;
  const ctx=shadowCanvas.getContext('2d');const gradient=ctx.createRadialGradient(64,64,8,64,64,63);
  gradient.addColorStop(0,'rgba(0,0,0,0.65)');gradient.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=gradient;ctx.fillRect(0,0,128,128);
  const shadowTexture=new THREE.CanvasTexture(shadowCanvas);
  const shadow=new THREE.Mesh(new THREE.PlaneGeometry(10.5,7.5),new THREE.MeshBasicMaterial({map:shadowTexture,transparent:true,depthWrite:false}));shadow.rotation.x=-Math.PI/2;shadow.position.y=-2.29;scene.add(shadow);

  let drag=false, lastX=0, rotation=0, pointerX=0, pointerY=0, visible=true, frame=0;
  function size() {
    const {width,height}=host.getBoundingClientRect();
    if(!width||!height)return;
    renderer.setSize(width,height,false);camera.aspect=width/height;
    camera.position.z=width<520?11.7:12.3;camera.lookAt(0,.05,0);camera.updateProjectionMatrix();
    render();
  }
  function render(){renderer.render(scene,camera);}
  const resizeObserver=new ResizeObserver(size);resizeObserver.observe(host);
  canvas.addEventListener('pointermove',event=>{
    if(event.pointerType!=='mouse'&&!drag)return;
    const r=canvas.getBoundingClientRect();pointerX=(event.clientX-r.left)/r.width-.5;pointerY=(event.clientY-r.top)/r.height-.5;
    if(drag){rotation+=(event.clientX-lastX)*.009;lastX=event.clientX;}
    if(drag||reduced){world.rotation.y=-.22+rotation+pointerX*.14;world.rotation.x=pointerY*.055;render();}
  });
  canvas.addEventListener('pointerdown',event=>{
    drag=true;lastX=event.clientX;canvas.setPointerCapture(event.pointerId);canvas.classList.add('is-dragging');
  });
  canvas.addEventListener('keydown',event=>{
    if(!['ArrowLeft','ArrowRight','Home'].includes(event.key))return;
    event.preventDefault();rotation=event.key==='Home'?0:rotation+(event.key==='ArrowLeft'?-.16:.16);
    world.rotation.y=-.22+rotation+pointerX*.14;render();
  });
  const release=()=>{drag=false;canvas.classList.remove('is-dragging');};
  canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);
  canvas.addEventListener('pointerleave',()=>{if(!drag){pointerX=0;pointerY=0;}});
  canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();useFallback();visible=false;cancelAnimationFrame(frame);frame=0;});
  const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible&&!frame&&!reduced)animate();},{rootMargin:'80px'});observer.observe(host);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden&&visible&&!frame&&!reduced)animate();});
  function animate(){
    if(!visible||document.hidden){frame=0;return;}
    const targetY=-.22+rotation+pointerX*.14;
    const targetX=pointerY*.055;
    if(Math.abs(world.rotation.y-targetY)>.00005||Math.abs(world.rotation.x-targetX)>.00005){
      world.rotation.y=THREE.MathUtils.lerp(world.rotation.y,targetY,.085);
      world.rotation.x=THREE.MathUtils.lerp(world.rotation.x,targetX,.075);
      render();
    }
    frame=requestAnimationFrame(animate);
  }
  size();render();host.classList.add('scene-ready');
  if(!reduced)animate();
  window.SpeedyScene={renderer,scene,reset(){rotation=0;pointerX=0;pointerY=0;if(reduced){world.rotation.set(0,-.22,0);render();}}};
  document.querySelector('#reset-engine')?.addEventListener('click',()=>window.SpeedyScene.reset());
})();
