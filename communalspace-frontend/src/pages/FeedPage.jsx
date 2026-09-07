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
    <div className="bg-cs-bg w-screen min-h-screen">
      <Navbar1 />
      <div className="pt-42 max-w-[1240px] mx-auto px-8 pb-16 grid grid-cols-[1fr_340px] gap-8 items-start">
        <main>
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
          />
        </main>

        <aside>
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
