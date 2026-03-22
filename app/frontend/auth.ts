import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { encryptPayload, decryptPayload } from "@/lib/crypto-server";

const HOST = process.env.NEXT_PUBLIC_HOST || "";
const PATH  = `http://${HOST}/auth`

type ISODateString = string

export interface DefaultSession {
  token?: any
  expires: ISODateString
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      name: "Credentials",
      credentials: {},
      async authorize() {
        console.log(PATH)
        try {
          const res = await fetch(PATH, { credentials: "include" })
          const data = await res.json() 

          if (!data?.encrypted) return  null;

          const decrypted = decryptPayload(data.encrypted)
            if (decrypted?.token) {
              let x = { id: "anon", token: decrypted.token}
              return  x
            }
            return  null
        } catch (error) {
          // console.error("Auth error:", error);
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
        if (user?.token) {
      token.token = user.token; 
    }
      return token;
    },
    async session({ session, token, user }) {
      if (token?.token){
        session.user.token = token.token;

      }
      return session;
    },
  },
  session: { strategy: "jwt" },
});
