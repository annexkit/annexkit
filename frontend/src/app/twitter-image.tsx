/**
 * Twitter / X card image — same content as the OpenGraph image, exported
 * separately because some clients pick the twitter-image entry first.
 *
 * Re-using the OpenGraph render keeps the two perfectly in sync; if we
 * ever want to ship a Twitter-specific variant (e.g. tighter copy, since
 * X truncates aggressively), branch from here.
 */

export {
  default,
  alt,
  size,
  contentType,
} from "./opengraph-image";
