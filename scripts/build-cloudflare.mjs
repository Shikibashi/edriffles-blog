import { spawnSync } from 'node:child_process';

const env = process.env;
const isCloudflarePages = env.CF_PAGES === '1';
const productionBranch = env.CF_PAGES_PRODUCTION_BRANCH || 'master';
const branch = env.CF_PAGES_BRANCH;

if (isCloudflarePages && !branch) {
	console.error('CF_PAGES_BRANCH is missing; refusing to guess whether this is a production build.');
	process.exit(1);
}

const isProduction = !isCloudflarePages || branch === productionBranch;
const script = isProduction ? 'build:production' : 'build:astro';

if (isProduction) {
	console.log(`Cloudflare production build on ${productionBranch}; publishing Standard.site records.`);
} else {
	console.log(`Cloudflare preview build on ${branch}; skipping Standard.site publishing.`);
}

const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const result = spawnSync(npmCommand, ['run', script], {
	stdio: 'inherit',
	env,
});

if (result.error) {
	console.error(`Unable to run npm: ${result.error.message}`);
	process.exit(1);
}

process.exit(result.status ?? 1);
