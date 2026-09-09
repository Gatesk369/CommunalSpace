import { useState } from "react";
import Navbar1 from "../components/Navbar1";
import AnnouncementBanner from "../components/AnnouncementBanner";
import PostComposer from "../components/PostComposer";
import PostCard from "../components/PostCard";
import NearbyBusinessesCard from "../components/NearbyBusinessesCard";
import CommunityAdminsCard from "../components/CommunityAdminsCard";
import MessagesBar from "../components/MessagesBar";

export default function FeedPage() {
  const [showBanner, setShowBanner] = useState(true);

  return (
    <div className="bg-cs-bg max-w-screen min-h-screen flex items-center justify-center p-4 sm:p-8">
      <Navbar1 />
      <div className="mt-24 pl-120 w-full grid grid-cols-[1.3fr_28rem] gap-8 mr-0">
        <main className="w-full">
          {showBanner && (
            <AnnouncementBanner
              message="Power shut off this week from 8am–7pm across Kisaasi, Kyanja."
              onDismiss={() => setShowBanner(false)}
            />
          )}
          <PostComposer />
          <PostCard
            authorName="Amara Muwonge"
            community="Kisaasi"
            timeAgo="2h ago"
            content="Anyone else notice the streetlight near the community hall is out again?"
            likeCount={14}
            commentCount={6}
          />
          <PostCard
            authorName="Sunrise Bakery"
            community="Kisaasi"
            timeAgo="5h ago"
            content="Fresh batch of cardamom rolls just came out of the oven 🍞"
            likeCount={41}
            commentCount={9}
            isBusiness
            media
          />
        </main>

        <aside className="flex flex-col gap-8">
          <NearbyBusinessesCard
            businesses={[
              { name: "Sunrise Bakery", initiallyFollowing: true },
              { name: "Kisaasi Hardware" },
              { name: "Heights Pharmacy" },
            ]}
          />
          <CommunityAdminsCard
            admins={[{ name: "Rita Nakato" }, { name: "David Okello" }]}
          />
          <MessagesBar unreadCount={13} />
        </aside>
      </div>
    </div>
  );
}
