/**
 * Thin axios wrapper for the builder endpoints.
 * All other requests continue to use the app-wide axios instance; this file
 * just centralises the URLs so they can be refactored in one place.
 */
import axios from 'axios';

export const CATALOGUE_URL = '/api/catalogue';

export async function fetchCatalogue() {
  const { data } = await axios.get(CATALOGUE_URL);
  return data.data;
}

export async function fetchWebsite(id) {
  const { data } = await axios.get(`/api/websites/${id}`);
  return data.data?.website || data.website;
}

export async function savePageTree(websiteId, pageId, tree) {
  const { data } = await axios.put(
    `/api/websites/${websiteId}/pages/${pageId}`,
    { tree },
  );
  return data.data?.page || data.page;
}

export async function savePageMeta(websiteId, pageId, { title, slug, order }) {
  const body = {};
  if (title !== undefined) body.title = title;
  if (slug  !== undefined) body.slug  = slug;
  if (order !== undefined) body.order = order;
  const { data } = await axios.put(
    `/api/websites/${websiteId}/pages/${pageId}`,
    body,
  );
  return data.data?.page || data.page;
}

export async function addPage(websiteId, { title, slug, tree }) {
  const { data } = await axios.post(
    `/api/websites/${websiteId}/pages`,
    { title, slug, content: '', tree },
  );
  return data.data?.page || data.page;
}

export async function deletePage(websiteId, pageId) {
  await axios.delete(`/api/websites/${websiteId}/pages/${pageId}`);
}

export async function updateWebsite(websiteId, patch) {
  const { data } = await axios.put(`/api/websites/${websiteId}`, patch);
  return data.data?.website || data.website;
}

export async function publishWebsite(websiteId) {
  const { data } = await axios.put(`/api/websites/${websiteId}/publish`);
  return data.data?.website || data.website;
}

export async function unpublishWebsite(websiteId) {
  const { data } = await axios.put(`/api/websites/${websiteId}/unpublish`);
  return data.data?.website || data.website;
}

/** URL that the iframe preview will hit. Token appended as a query string
 *  so the iframe request can carry auth — the backend's JWT middleware
 *  accepts tokens from the `access_token` query parameter.
 *
 *  We use an absolute URL pointing at the backend directly because CRA's
 *  dev-server proxy intercepts `text/html` requests and serves index.html
 *  instead of proxying them. In production, REACT_APP_BACKEND_URL can be
 *  left empty so the same-origin URL is used. */
export function previewUrl(websiteId, pageSlug, token) {
  const base = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5050';
  const path = `/api/websites/${websiteId}/preview${pageSlug ? '/' + pageSlug : ''}`;
  return token ? `${base}${path}?access_token=${encodeURIComponent(token)}`
               : `${base}${path}`;
}
