# use the official Bun image
# see all versions at https://hub.docker.com/r/oven/bun/tags
FROM oven/bun:1 AS base
WORKDIR /usr/src/app

# install dependencies into temp directory
# this will cache them and speed up future builds
FROM base AS install
RUN mkdir -p /temp/dev
COPY package.json bun.lock /temp/dev/
RUN cd /temp/dev && bun install --frozen-lockfile

# install with --production (exclude devDependencies)
FROM base AS production
RUN mkdir -p /temp/prod
COPY package.json bun.lock /temp/prod/
RUN cd /temp/prod && bun install --frozen-lockfile --production

# copy node_modules from temp directory and build the app
FROM base AS prerelease
COPY --from=install /temp/dev/node_modules node_modules
COPY . .
# [optional] run tests and build the Next.js app
ENV NODE_ENV=production
RUN bun test
RUN bun run build

# prepare final image using production dependencies and built output
FROM base AS release
COPY --from=production /temp/prod/node_modules node_modules
COPY --from=prerelease /usr/src/app/.next ./.next
COPY --from=prerelease /usr/src/app/package.json .
COPY --from=prerelease /usr/src/app/next.config.ts .
# If you have a public folder, copy that too.
COPY --from=prerelease /usr/src/app/public ./public
# run the app using the Next.js start script
USER bun
EXPOSE 3000/tcp
ENTRYPOINT [ "bun", "run", "start" ]
