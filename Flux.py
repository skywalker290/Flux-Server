import random
import torch
import numpy as np
from PIL import Image
import nodes
from nodes import NODE_CLASS_MAPPINGS
from totoro_extras import nodes_custom_sampler
from totoro import model_management

DualCLIPLoader = NODE_CLASS_MAPPINGS["DualCLIPLoader"]()
UNETLoader = NODE_CLASS_MAPPINGS["UNETLoader"]()
RandomNoise = nodes_custom_sampler.NODE_CLASS_MAPPINGS["RandomNoise"]()
BasicGuider = nodes_custom_sampler.NODE_CLASS_MAPPINGS["BasicGuider"]()
KSamplerSelect = nodes_custom_sampler.NODE_CLASS_MAPPINGS["KSamplerSelect"]()
BasicScheduler = nodes_custom_sampler.NODE_CLASS_MAPPINGS["BasicScheduler"]()
SamplerCustomAdvanced = nodes_custom_sampler.NODE_CLASS_MAPPINGS["SamplerCustomAdvanced"]()
VAELoader = NODE_CLASS_MAPPINGS["VAELoader"]()
VAEDecode = NODE_CLASS_MAPPINGS["VAEDecode"]()
EmptyLatentImage = NODE_CLASS_MAPPINGS["EmptyLatentImage"]()

with torch.inference_mode():
    clip = DualCLIPLoader.load_clip("t5xxl_fp8_e4m3fn.safetensors", "clip_l.safetensors", "flux")[0]
    unet = UNETLoader.load_unet("flux1-schnell.safetensors", "fp8_e4m3fn")[0]
    vae = VAELoader.load_vae("ae.sft")[0]

def closestNumber(n, m):
    q = int(n / m)
    n1 = m * q
    if (n * m) > 0:
        n2 = m * (q + 1)
    else:
        n2 = m * (q - 1)
    if abs(n - n1) < abs(n - n2):
        return n1
    return n2

# def generate_image():
#     # data = request.get_json()
#     # prompt = data.get("prompt")
#     # height = data.get("height")
#     # width = data.get("width")

#     prompt = "random image"
#     height = 400
#     width = 300
#     with torch.inference_mode():
#         positive_prompt = prompt
#         width = width
#         height = height
#         seed = 0
#         steps = 4
#         sampler_name = "euler"
#         scheduler = "simple"

#         if seed == 0:
#             seed = random.randint(0, 18446744073709551615)
#         print(seed)

#         cond, pooled = clip.encode_from_tokens(clip.tokenize(positive_prompt), return_pooled=True)
#         cond = [[cond, {"pooled_output": pooled}]]
#         noise = RandomNoise.get_noise(seed)[0]
#         guider = BasicGuider.get_guider(unet, cond)[0]
#         sampler = KSamplerSelect.get_sampler(sampler_name)[0]
#         sigmas = BasicScheduler.get_sigmas(unet, scheduler, steps, 1.0)[0]
#         latent_image = EmptyLatentImage.generate(closestNumber(width, 16), closestNumber(height, 16))[0]
#         sample, sample_denoised = SamplerCustomAdvanced.sample(noise, guider, sampler, sigmas, latent_image)
#         model_management.soft_empty_cache()
#         decoded = VAEDecode.decode(vae, sample)[0].detach()
#         Image.fromarray(np.array(decoded*255, dtype=np.uint8)[0]).save("Output_images/flux.png")

#     Image.fromarray(np.array(decoded*255, dtype=np.uint8)[0])

import random
import torch
import numpy as np
from PIL import Image

def generate_image():
    prompt = "random image"
    height = 400
    width = 300

    with torch.inference_mode():
        positive_prompt = prompt
        seed = 0
        steps = 2
        sampler_name = "euler"
        scheduler = "simple"

        if seed == 0:
            seed = random.randint(0, 18446744073709551615)
        print(seed)

        cond, pooled = clip.encode_from_tokens(clip.tokenize(positive_prompt), return_pooled=True)
        cond = [[cond, {"pooled_output": pooled}]]
        
        # Get noise and guider
        noise = RandomNoise.get_noise(seed)[0]
        guider = BasicGuider.get_guider(unet, cond)[0]

        # Retrieve the sampler and scheduling sigmas
        sampler = KSamplerSelect.get_sampler(sampler_name)[0]
        sigmas = BasicScheduler.get_sigmas(unet, scheduler, steps, 1.0)[0]

        # Reduce latent image size to fit within GPU capacity
        latent_image = EmptyLatentImage.generate(closestNumber(width, 16), closestNumber(height, 16))[0]

        # Sampling process with memory clearing after intensive operations
        sample, _ = SamplerCustomAdvanced.sample(noise, guider, sampler, sigmas, latent_image)
        
        # Clear cache before decoding to free up memory
        torch.cuda.empty_cache()
        
        decoded = VAEDecode.decode(vae, sample)[0].detach()
        
        # Convert and save image
        img_array = np.array(decoded * 255, dtype=np.uint8)[0]
        Image.fromarray(img_array).save("Output_images/flux.png")
    


generate_image()