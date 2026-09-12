import { useState, useEffect } from "react";
import AnnouncementBanner from "../components/AnnouncementBanner";
import PostComposer from "../components/PostComposer";
import PostCard from "../components/PostCard";
import NearbyBusinessesCard from "../components/NearbyBusinessesCard";
import CommunityAdminsCard from "../components/CommunityAdminsCard";
import MessagesBar from "../components/MessagesBar";
import { getPosts } from "../api/posts";
import { getBusinesses } from "../api/businesses";
import { getCurrentUser } from "../api/accounts";
import { getCommunityDetail } from "../api/communities";
import { getAnnouncements } from "../api/announcements";
import { formatTimeAgo } from "../utils/time";

export default function FeedPage() {
  const [showBanner, setShowBanner] = useState(true);
  const [posts, setPosts] = useState([]);
  const [businesses, setBusinesses] = useState([]);
  const [admins, setAdmins] = useState([]);
  const [announcement, setAnnouncement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadFeed() {
      try {
        const [postsData, businessesData, currentUser, announcementsData] =
          await Promise.all([
            getPosts(),
            getBusinesses(),
            getCurrentUser(),
            getAnnouncements(),
          ]);

        setPosts(postsData.results);
        setBusinesses(businessesData);

        if (currentUser.community) {
          const community = await getCommunityDetail(currentUser.community);
          setAdmins(community.admin_names);

          const relevant = announcementsData.filter((a) =>
            a.communities.includes(currentUser.community),
          );
          if (relevant.length > 0) {
            setAnnouncement(relevant[0]);
          }
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadFeed();
  }, []);

  function handlePostCreated(newPost) {
    setPosts((prev) => [newPost, ...prev]);
  }

  return (
    <div className="w-full grid grid-cols-[1.3fr_28rem] gap-8 p-4 sm:p-8">
      <main className="w-full">
        {showBanner && announcement && (
          <AnnouncementBanner
            urgency={announcement.urgency}
            message={announcement.title}
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
          businesses={businesses.map((b) => ({
            id: b.id,
            name: b.name,
            initiallyFollowing: b.is_following,
          }))}
        />
        <CommunityAdminsCard admins={admins} />
        <MessagesBar unreadCount={13} />
      </aside>
    </div>
  );
}
