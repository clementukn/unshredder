import sys
import timeit
from PIL import Image


def get_matching_score(shred_left, shred_right, image, shred_width):
	"""
	Returns the number of matching pixels between 2 shreds
	"""
	if shred_left == shred_right:
		return -1

	width, height = image.size[0], image.size[1]
	data = image.getdata()
	matches = [abs(data[h * width + (shred_left + 1) * shred_width - 1] \
				- data[h * width + shred_right * shred_width]) < 20 for h in range(height)]
	return sum(matches)


def get_match_matrix(image, shred_width):
	"""
	Returns the matrix of the matching scores between every pair of shreds
	"""
	shreds_cnt = image.size[0] / shred_width
	matrix = [[get_matching_score(x, y, image, shred_width) for y in range(shreds_cnt)] for x in range(shreds_cnt)]
	return matrix


def get_edges(shred):
	"""
	Returns the edges of a shred. A shred can be composed of other shreds
	"""
	if not len(shred):
		raise Exception("error")
	elif len(shred) == 1:
		return (shred[0], shred[0])
	else:
		return (shred[0], shred[-1])


def get_ordering(image, shred_width):
	"""
	returns the list of shred indices to unshred image
	"""
	shreds = [[i] for i in range(image.size[0] / shred_width)]
	match_matrix = get_match_matrix(image, shred_width)

	# look for best matching shreds, remove from list of shreds, assemble into new shred
	# and put back into list
	while len(shreds) > 1:
		best_match = -1
		best_shreds = (-1, -1)
		for idx1, s1 in enumerate(shreds):
			l_edge1, r_edge1 = get_edges(s1)
			for idx2, s2 in enumerate(shreds):
				if s1 == s2: continue
				l_edge2, r_edge2 = get_edges(s2)
				
				if match_matrix[r_edge1][l_edge2] > best_match:
					best_match = match_matrix[r_edge1][l_edge2]
					best_shreds = (s1, s2)

		sl, sr = best_shreds
		shreds.remove(sl)
		shreds.remove(sr)
		shreds.append(sl + sr)
		
	return shreds
	

def create_image(img_src, shreds_order, shred_size):
	""" 
	Create the unshredded image from the original shred and computed ordered shreds 
	"""
	img_unshred = Image.new("RGBA", img_src.size)

	for idx, s in enumerate(shreds_order):
		curr_shred = img_src.crop((s * shred_size, 0, s * shred_size + shred_size, img_src.size[1]))
		destination_point = (idx * shred_size, 0)
		img_unshred.paste(curr_shred, destination_point)
	return img_unshred


def detect_shred_width(image):
	"""
	Bonus : detect shred width. Assume shreds are larger than 1 pixel
	"""
	threshold = 0.20 # deviation of 20% from average
	ref_score = get_matching_score(0, 1, image, 1)
	for i in range(2, image.size[0] / 2):
		score = get_matching_score(0, 1, image, i)
		if (abs(score - ref_score) > threshold * ref_score):
			return i
		ref_score = score
	return -1
		

def unshred(in_filename):
	"""
	entry point function to unshred a given picture
	"""
	img_src = Image.open(in_filename)
	image = img_src.convert("L")

	shred_width = detect_shred_width(image)
	if shred_width == -1:
		print "Couldn't detect shred width"
		exit()
		
	shreds_order = get_ordering(image, shred_width)

	unshredded_img = create_image(img_src, shreds_order[0], shred_width)
	unshredded_img.save(in_filename + "_unshredded.png", "PNG")


if len(sys.argv) <= 1:
	print "Please, provide the filename as an argument."
	exit()

start = timeit.default_timer()
unshred(sys.argv[1])
end = timeit.default_timer()

print "image unshredded in", end-start, "seconds"