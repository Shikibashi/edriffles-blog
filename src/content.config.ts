import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const optionalDate = z.preprocess(
	(value) => (value === '' ? undefined : value),
	z.coerce.date().optional(),
);

const blog = defineCollection({
	// Load Markdown and MDX files in the `src/content/blog/` directory.
	loader: glob({
		base: './src/content/blog',
		pattern: '**/*.{md,mdx}',
		// Sveltia stores posts as <slug>/index.md so images can live beside them.
		// Keep the public content ID (and therefore the URL) equal to <slug>.
		generateId: ({ entry }) =>
			entry.replace(/\.(?:md|mdx)$/, '').replace(/\/index$/, ''),
	}),
	// Type-check frontmatter using a schema
	schema: ({ image }) =>
		z.object({
			title: z.string().optional(),
			description: z.string().optional(),
			// Transform string to Date object
			pubDate: z.coerce.date(),
			updatedDate: optionalDate,
			heroImage: z.optional(image()),
			heroImageAlt: z.string().optional(),
		}),
});

export const collections = { blog };
