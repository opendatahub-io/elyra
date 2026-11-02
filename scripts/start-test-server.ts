/*
 * Copyright 2018-2025 Elyra Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { exec, spawn } from 'child_process';
import fs from 'fs';
import http from 'http';
import path from 'path';

const config = path.join(__dirname, '..', 'cypress', 'test-config.py');
const jupyter = exec(`jupyter lab --config ${config}`);

const CONTAINER_NAME = 'minio_test';
const MINIO_PORT = 9000;

const logDir = path.join(__dirname, '..', 'build', 'cypress');
const jupyterLog = fs.createWriteStream(path.join(logDir, 'jupyter.log'));
jupyter.stderr?.pipe(jupyterLog);
const dockerLog = fs.createWriteStream(path.join(logDir, 'docker.log'));

/**
 * Check if an S3-compatible server is already reachable on port 9000.
 * Accepts real MinIO (200 health), moto server (any HTTP response), or any
 * other S3-compatible service.  Returns a Promise that resolves to true when
 * the server responds to an HTTP request (any status code), false otherwise.
 */
const isMinioRunning = (): Promise<boolean> =>
  new Promise((resolve) => {
    const req = http.get(
      `http://127.0.0.1:${MINIO_PORT}/minio/health/live`,
      (res) => {
        // Accept any HTTP response: 200 from real MinIO, 404 from moto server, etc.
        resolve(res.statusCode !== undefined);
        res.resume();
      }
    );
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(false);
    });
    req.on('error', () => resolve(false));
  });

// Track whether this process started the MinIO container so teardown only
// kills containers that we own (not a container started by CI or the user).
let minioStartedByUs = false;

const handleTeardown = (): void => {
  if (minioStartedByUs) {
    spawn('docker', ['kill', CONTAINER_NAME]);
  }
  process.exit();
};

process.on('SIGINT', handleTeardown);
process.on('SIGTERM', handleTeardown);

// Only start a Docker container when MinIO is not already available (e.g. in
// local development).  In CI the minio container is started before this script.
isMinioRunning().then((already) => {
  if (already) {
    dockerLog.write('MinIO already running on port 9000; skipping Docker.\n');
    return;
  }

  minioStartedByUs = true;
  const docker = spawn('docker', [
    'run',
    '--rm',
    '--name',
    CONTAINER_NAME,
    '-p',
    `${MINIO_PORT}:${MINIO_PORT}`,
    'minio/minio',
    'server',
    '/data'
  ]);
  docker.stderr.pipe(dockerLog);
});
