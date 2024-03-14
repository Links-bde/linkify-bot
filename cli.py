import linkify_lib
import asyncio


async def main():
	login = input("login: ")
	print(f"processing {login}")
	image = await asyncio.to_thread(linkify_lib.linkify_user, login)
	image.save(f"{login}_link.png")
	image.show()


if __name__ == "__main__":
	asyncio.run(main())


