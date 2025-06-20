import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    baseline: { executor: 'constant-vus', vus: 10, duration: '1m' },
    stress: { executor: 'ramping-vus', stages: [ { duration: '1m', target: 50 }, { duration: '2m', target: 200 } ] },
    spike: { executor: 'ramping-arrival-rate', startRate: 0, timeUnit: '1s', stages: [ { duration: '10s', target: 100 }, { duration: '10s', target: 0 } ], preAllocatedVUs: 100 },
    soak: { executor: 'constant-vus', vus: 20, duration: '5m' }
  }
};

const BASE_URL = 'http://localhost:8000';
const users = [{"username": "dev_user", "password": "dev_pass"}];

export default function () {
  const user = users[Math.floor(Math.random() * users.length)];
  const loginRes = http.post(`${BASE_URL}/token`, { username: user.username, password: user.password });
  check(loginRes, { 'login ok': r => r.status === 200 });
  const token = loginRes.json('access_token');
  const params = { headers: { Authorization: `Bearer ${token}` } };
  http.get(`${BASE_URL}/users/me`, params);
  sleep(1);
}
