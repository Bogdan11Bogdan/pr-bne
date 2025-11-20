import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js';

const canvas = document.getElementById('scene');
const scoreLabel = document.querySelector('#score-display strong');
const timerLabel = document.querySelector('#timer-display strong');

const renderer = new THREE.WebGLRenderer({ antialias: true, canvas, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new THREE.Scene();
scene.background = new THREE.Color('#070914');
scene.fog = new THREE.FogExp2('#070914', 0.025);

const camera = new THREE.PerspectiveCamera(60, 16 / 9, 0.1, 1000);
camera.position.set(0, 6, 14);
scene.add(camera);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.target.set(0, 2, 0);

const hemiLight = new THREE.HemisphereLight('#8ef7ff', '#1a1a2a', 0.65);
scene.add(hemiLight);

const dirLight = new THREE.DirectionalLight('#fff6d9', 1.2);
dirLight.position.set(4, 8, 6);
dirLight.castShadow = true;
scene.add(dirLight);

renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const groundGeometry = new THREE.CylinderGeometry(18, 18, 1, 40, 1, true);
const groundMaterial = new THREE.MeshStandardMaterial({
  color: '#11182d',
  roughness: 0.9,
  metalness: 0.05,
});
const ground = new THREE.Mesh(groundGeometry, groundMaterial);
ground.receiveShadow = true;
ground.position.y = -0.6;
scene.add(ground);

const grid = new THREE.GridHelper(24, 24, '#1ef9ff', '#1f2c46');
grid.position.y = 0.01;
scene.add(grid);

const ringGeometry = new THREE.RingGeometry(20.8, 22, 64, 1);
const ringMaterial = new THREE.MeshBasicMaterial({ color: '#0e1225', side: THREE.DoubleSide, opacity: 0.4, transparent: true });
const ring = new THREE.Mesh(ringGeometry, ringMaterial);
ring.rotation.x = -Math.PI / 2;
ring.position.y = -0.59;
scene.add(ring);

const playerGeometry = new THREE.BoxGeometry(1.2, 1.2, 1.2);
const playerMaterial = new THREE.MeshStandardMaterial({
  color: '#7cf2c4',
  metalness: 0.2,
  roughness: 0.3,
  emissive: '#17443a',
  emissiveIntensity: 0.5,
});
const player = new THREE.Mesh(playerGeometry, playerMaterial);
player.castShadow = true;
player.position.y = 1;
scene.add(player);

const playerVelocity = new THREE.Vector3();
let onGround = true;

const tokenGeometry = new THREE.OctahedronGeometry(0.6);
const tokenMaterial = new THREE.MeshStandardMaterial({
  color: '#f2d57c',
  metalness: 0.6,
  roughness: 0.2,
  emissive: '#3d2f13',
  emissiveIntensity: 0.8,
});
const tokens = [];

function spawnToken() {
  const mesh = new THREE.Mesh(tokenGeometry, tokenMaterial.clone());
  mesh.castShadow = true;
  mesh.position.set(
    THREE.MathUtils.randFloatSpread(18),
    THREE.MathUtils.randFloat(0.8, 3),
    THREE.MathUtils.randFloatSpread(18)
  );
  mesh.userData.baseY = mesh.position.y;
  scene.add(mesh);
  tokens.push(mesh);
}

for (let i = 0; i < 8; i += 1) {
  spawnToken();
}

const keys = new Set();
window.addEventListener('keydown', (event) => keys.add(event.code));
window.addEventListener('keyup', (event) => keys.delete(event.code));

let score = 0;
let timeLeft = 60;
let lastTime = performance.now();

function updateHUD() {
  scoreLabel.textContent = score.toString();
  timerLabel.textContent = Math.max(0, Math.floor(timeLeft)).toString();
}

updateHUD();

function resizeRenderer() {
  const { width, height } = canvas.getBoundingClientRect();
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

resizeRenderer();
window.addEventListener('resize', resizeRenderer);

const clock = new THREE.Clock();

function handleMovement(delta) {
  const acceleration = 18 * delta;
  const damping = Math.pow(0.88, delta * 60);
  const maxSpeed = 10;

  if (keys.has('KeyW') || keys.has('ArrowUp')) playerVelocity.z -= acceleration;
  if (keys.has('KeyS') || keys.has('ArrowDown')) playerVelocity.z += acceleration;
  if (keys.has('KeyA') || keys.has('ArrowLeft')) playerVelocity.x -= acceleration;
  if (keys.has('KeyD') || keys.has('ArrowRight')) playerVelocity.x += acceleration;

  if (onGround && (keys.has('Space') || keys.has('ShiftLeft'))) {
    playerVelocity.y = 8;
    onGround = false;
  }

  playerVelocity.y -= 20 * delta;

  playerVelocity.x = THREE.MathUtils.clamp(playerVelocity.x, -maxSpeed, maxSpeed);
  playerVelocity.z = THREE.MathUtils.clamp(playerVelocity.z, -maxSpeed, maxSpeed);

  player.position.addScaledVector(playerVelocity, delta);

  if (player.position.y <= 1) {
    player.position.y = 1;
    playerVelocity.y = 0;
    onGround = true;
  }

  playerVelocity.x *= damping;
  playerVelocity.z *= damping;
}

function wrapPosition(object, limit = 18) {
  ['x', 'z'].forEach((axis) => {
    if (object.position[axis] > limit) object.position[axis] = -limit;
    if (object.position[axis] < -limit) object.position[axis] = limit;
  });
}

function updateTokens(delta) {
  tokens.forEach((token) => {
    token.rotation.x += delta * 1.2;
    token.rotation.y -= delta * 1.8;

    const bounce = Math.sin(clock.elapsedTime * 2 + token.id) * 0.15;
    token.position.y = token.userData.baseY + bounce;

    const distance = token.position.distanceTo(player.position);
    if (distance < 1.4) {
      score += 10;
      token.position.set(
        THREE.MathUtils.randFloatSpread(18),
        THREE.MathUtils.randFloat(0.8, 3),
        THREE.MathUtils.randFloatSpread(18)
      );
      token.userData.baseY = token.position.y;
      token.material.color.setHSL(Math.random(), 0.6, 0.6);
      updateHUD();
    }
  });
}

const particles = [];
const sparkleGeometry = new THREE.SphereGeometry(0.05, 6, 6);
const sparkleMaterial = new THREE.MeshBasicMaterial({ color: '#7cf2c4' });
for (let i = 0; i < 120; i += 1) {
  const mesh = new THREE.Mesh(sparkleGeometry, sparkleMaterial);
  mesh.position.set(
    THREE.MathUtils.randFloatSpread(40),
    THREE.MathUtils.randFloat(4, 18),
    THREE.MathUtils.randFloatSpread(40)
  );
  scene.add(mesh);
  particles.push(mesh);
}

function updateParticles(delta) {
  particles.forEach((particle, index) => {
    particle.position.y -= 0.5 * delta;
    if (particle.position.y < 1) particle.position.y = THREE.MathUtils.randFloat(6, 18);
    particle.position.x += Math.sin(clock.elapsedTime + index) * 0.01;
  });
}

function animate(now) {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();
  const elapsed = now - lastTime;
  lastTime = now;

  if (timeLeft > 0) {
    timeLeft -= elapsed / 1000;
    if (timeLeft < 0) timeLeft = 0;
    updateHUD();
  }

  handleMovement(delta);
  wrapPosition(player);
  updateTokens(delta);
  updateParticles(delta);

  controls.update();
  renderer.render(scene, camera);
}

requestAnimationFrame(animate);

const overlay = document.querySelector('.card p');
function showStatusMessage(message) {
  overlay.textContent = message;
  overlay.style.color = '#ffffff';
  overlay.animate(
    [
      { opacity: 0.4, transform: 'translateY(6px)' },
      { opacity: 1, transform: 'translateY(0)' },
    ],
    { duration: 260, easing: 'ease-out' }
  );
}

showStatusMessage('Zbieraj kryształki i nie wypadaj poza pierścień!');
