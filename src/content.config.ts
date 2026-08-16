import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const optionalDate = z.preprocess(
	(value) => (value === '' ? undefined : value),
	z.coerce.date().optional(),
);

const blog = defineCollection({
	// Load written Markdown and MDX posts from the `src/content/blog/` directory.
	loader: glob({
		base: './src/content/blog',
		pattern: '**/*.{md,mdx}',
		// Keep the public content ID equal to the file path.
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

const gallery = defineCollection({
	loader: glob({
		base: './src/content/gallery',
		pattern: '**/*.md',
		generateId: ({ entry }) => entry.replace(/\.md$/, ''),
	}),
	schema: ({ image }) =>
		z.object({
			image: image(),
			alt: z.string().optional(),
		}),
});

export const collections = { blog, gallery };
