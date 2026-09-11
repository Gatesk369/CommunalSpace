import { useState, useEffect } from "react";
import AnnouncementBanner from "../components/AnnouncementBanner";
import PostComposer from "../components/PostComposer";
import PostCard from "../components/PostCard";
import NearbyBusinessesCard from "../components/NearbyBusinessesCard";
import CommunityAdminsCard from "../components/CommunityAdminsCard";
import MessagesBar from "../components/MessagesBar";
import { getPosts } from "../api/posts";
import { formatTimeAgo } from "../utils/time";

export default function FeedPage() {
  const [showBanner, setShowBanner] = useState(true);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getPosts()
      .then((data) => setPosts(data.results))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  function handlePostCreated(newPost) {
    setPosts((prev) => [newPost, ...prev]);
  }

  return (
    <div className="w-full grid grid-cols-[1.3fr_28rem] gap-8 p-4 sm:p-8">
      <main className="w-full">
        {showBanner && (
          <AnnouncementBanner
            message="Power shut off this week from 8am–7pm across Kisaasi, Kyanja."
            onDismiss={() => setShowBanner(false)}
          />
        )}
        <PostComposer onPostCreated={handlePostCreated} />

        {loading && <p className="text-cs-muted text-sm">Loading posts...</p>}
        {error && <p className="text-cs-red text-sm">{error}</p>}
        {!loading && !error && posts.length === 0 && (
          <p className="text-cs-muted text-sm">
            No posts yet. Be the first to share something!
          </p>
        )}

        {posts.map((post) => (
          <PostCard
            key={post.id}
            id={post.id}
            authorName={post.author_name}
            community={post.community_name}
            timeAgo={formatTimeAgo(post.created_at)}
            content={post.content}
            media={post.media}
            likeCount={post.like_count}
            commentCount={post.comment_count}
            isBusiness={post.post_type === "business"}
            userHasLiked={post.user_has_liked}
          />
        ))}
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
  );
}
