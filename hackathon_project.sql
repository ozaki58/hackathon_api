-- --------------------------------------------------------
-- ホスト:                          127.0.0.1
-- サーバーのバージョン:                   8.0.35 - MySQL Community Server - GPL
-- サーバー OS:                      Win64
-- HeidiSQL バージョン:               12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- hackathon_project のデータベース構造をダンプしています
CREATE DATABASE IF NOT EXISTS `hackathon_project` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `hackathon_project`;

-- 一旦全てのテーブルを削除
DROP TABLE IF EXISTS `characters`;
DROP TABLE IF EXISTS `characters_status`;
DROP TABLE IF EXISTS `chats`;
DROP TABLE IF EXISTS `emojis`;
DROP TABLE IF EXISTS `goals`;
DROP TABLE IF EXISTS `goal_quests`;
DROP TABLE IF EXISTS `quests`;
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `user_emojis`;
DROP TABLE IF EXISTS `user_coins`;
DROP TABLE IF EXISTS `user_goals`;
DROP TABLE IF EXISTS `goal_chats`;


--  テーブル hackathon_project.characters の構造をダンプしています
CREATE TABLE IF NOT EXISTS `characters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `prompt` varchar(1000) NOT NULL,
  `image` varchar(255) NOT NULL,  -- blobからvarcharに変更
  `genre_id` varchar(50) NOT NULL,
  `price` int NOT NULL,
  `detail` varchar(1000),  -- detailカラムを追加
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.characters: ~2 rows (約) のデータをダンプしています
INSERT INTO `characters` (`id`, `name`, `prompt`, `image`, `genre_id`, `price`, `detail`) VALUES
(1, 'リサ', 'あなたはとにかく優しい性格で、人をよく褒めるメンターです', 'character/character1.png', '1', 1200, 'リサは、モンドの騎士団の団長である。彼女は、騎士団の団長として、モンドの平和を守るために、日々奮闘している。'),
(2, '薫', 'あなたはとにかく優しい性格で、人をよく褒めるメンターです', 'character/character2.png', '1', 3000, '薫は、モンドの騎士団の団長である。彼女は、騎士団の団長として、モンドの平和を守るために、日々奮闘している。'),
(3, 'ミツキ', 'あなたはとにかく優しい性格で、人をよく褒めるメンターです', 'character/character3.png', '2', 3000, 'みつきは、モンドの騎士団の団長である。彼女は、騎士団の団長として、モンドの平和を守るために、日々奮闘している。'),
(4, '愛', 'あなたはとにかく優しい性格で、人をよく褒めるメンターです', 'character/character4.png', '2', 3000, '薫は、モンドの騎士団の団長である。彼女は、騎士団の団長として、モンドの平和を守るために、日々奮闘している。'),
(5, 'シスター', 'あなたはとにかく優しい性格で、人をよく褒めるメンターです', 'character/character1.png', '3', 3000, NULL),
(6, 'にゃー', 'あなたはとにかく優しい性格で、人をよく褒めるメンターです', 'character/character2.png', '4', 6000, NULL);

--  テーブル hackathon_project.characters_status の構造をダンプしています
CREATE TABLE IF NOT EXISTS `characters_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `character_id` int NOT NULL,
  `is_favored` tinyint NOT NULL DEFAULT '0',
  `is_unlocked` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `FK__users_characters` (`user_id`),
  KEY `FK__characters` (`character_id`),
  CONSTRAINT `FK__characters` FOREIGN KEY (`character_id`) REFERENCES `characters` (`id`),
  CONSTRAINT `FK__users_characters` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.characters_status: ~2 rows (約) のデータをダンプしています
INSERT INTO `characters_status` (`id`, `user_id`, `character_id`, `is_favored`, `is_unlocked`) VALUES
	(1, 1, 1, 1, 1),
	(2, 1, 2, 0, 1);

--  テーブル hackathon_project.chats の構造をダンプしています
CREATE TABLE IF NOT EXISTS `chats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL DEFAULT '0',
  `character_id` int NOT NULL DEFAULT '0',
  `content` varchar(3000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT (now()),
  `sender_type` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `FK__users_chats` (`user_id`),
  KEY `FK__characters_chats` (`character_id`),
  CONSTRAINT `FK__characters_chats` FOREIGN KEY (`character_id`) REFERENCES `characters` (`id`),
  CONSTRAINT `FK__users_chats` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.chats: ~24 rows (約) のデータをダンプしています
INSERT INTO `chats` (`id`, `user_id`, `character_id`, `content`, `created_at`, `sender_type`) VALUES
	(1, 1, 1, '東京大学に合格したい', '2023-12-26 22:21:14', 0),
	(2, 1, 1, '東京大学に合格したい', '2023-12-26 22:25:34', 0),
	(3, 1, 1, 'モチベーションがわかない', '2023-12-26 22:45:46', 0),
	(4, 1, 1, 'モチベーションがわかない', '2023-12-26 22:54:04', 0),
	(5, 1, 1, 'モチベーションがわかない', '2023-12-26 23:05:15', 0),
	(6, 1, 1, 'モチベーションがわからないということは、やる気や意欲が湧かない状態を指しているかもしれません。モチベーションがわからない理由は人それぞれですが、以下のようなことが考えられます。\n\n1. 目標が明確でない：何のために何をするのかが明確でないと、モチベーションが湧きにくいことがあります。自分の目標ややりたいことを整理してみると良いでしょう。\n\n2. 疲れやストレス：疲れやストレスがたまっていると、モチベーションが低下することがあります。十分な休息やストレス解消を心がけることが大切です。\n\n3. 環境や人間関係：周囲の環境や人間関係がモチベーションに影響を与えることがあります。良い環境や支え合える人間関係を整えることが大切です。\n\n4. 自己肯定感の低さ：自分に自信が持てず、自己肯定感が低いとモチベーションがわかないことがあります。自分を認め、自分を大切にすることが大切です。\n\nこれらの要因を考えながら、自分自身の状況を振り返り、モチベーションを取り戻すための方法を見つけてみてください。また、専門家や信頼できる人に相談することも有効です。', '2023-12-26 23:05:15', 1),
	(7, 1, 1, 'やるきがでない', '2023-12-26 23:13:33', 0),
	(8, 1, 1, 'やる気が出ないと感じることはありますね。それはとても辛いことですが、その原因を探ってみることが大切です。まずは自分の心や体がどう感じているのかをじっくりと考えてみましょう。ストレスや疲れ、不安などが原因であることもあります。\n\nまた、目標ややりたいことが明確でない場合もやる気が出なくなることがあります。自分の目標ややりたいことを整理し、それに向かって少しずつ行動してみることも大切です。\n\nもし状況が改善しない場合は、専門家やカウンセラーに相談することも一つの方法です。自分の気持ちに向き合い、必要ならばサポートを受けながら、少しずつ前に進んでいきましょう。', '2023-12-26 23:13:33', 1),
	(9, 1, 1, 'やるきがでない', '2023-12-26 23:44:59', 0),
	(10, 1, 1, 'そんな時もありますね。でも大丈夫ですよ。自分を責めずに、少しずつ進めることから始めてみましょう。あなたのやる気が出るきっかけを見つけるために、一緒に考えてみませんか？自分のやりたいことや興味を見つけることが、やる気を取り戻す第一歩かもしれません。', '2023-12-26 23:44:59', 1),
	(11, 1, 1, '眠りにつけないよ', '2023-12-27 00:14:59', 0),
	(12, 1, 1, '大丈夫ですよ。眠れないときは、リラックスするための方法を試してみると良いかもしれません。例えば、深呼吸やストレッチ、リラックスした音楽を聴くことなどが効果的です。また、寝る前にスマートフォンやパソコンの画面を見るのを避けることも大切です。少しずつ試してみて、自分に合った方法を見つけてみてくださいね。', '2023-12-27 00:14:59', 1),
	(13, 1, 1, 'ビールを飲んでるよ', '2023-12-27 00:25:07', 0),
	(14, 1, 1, '飲んでいるのですね。リラックスしたい時には、ビールを楽しむのも良い方法ですね。ただし、飲酒は適量を守ることが大切ですので、飲みすぎには注意してくださいね。また、飲酒後には安全に帰宅することや、二日酔いにならないように水分補給をすることも大切です。楽しい時間を過ごしてくださいね。', '2023-12-27 00:25:07', 1),
	(15, 1, 1, '俺が何を飲んでいるか答えて', '2023-12-27 00:34:17', 0),
	(16, 1, 1, '申し訳ありませんが、お酒の摂取状況についてはサポートできません。何か他にお手伝いできることはありますか？', '2023-12-27 00:34:17', 0),
	(17, 1, 1, 'どうして', '2023-12-27 00:34:38', 0),
	(18, 1, 1, '申し訳ありません、私はアドバイスを提供することができますが、個々の行動についての判断はできません。ただし、自分の行動が自分自身や他の人に害を及ぼさないように注意することが大切です。自分の安全と健康を第一に考えて行動することをお勧めします。何かお困りのことがあれば、遠慮なくお知らせください。お手伝いできることがあれば喜んでサポートさせていただきます。', '2023-12-27 00:34:38', 1),
	(19, 1, 1, 'あなたのは性格は？', '2023-12-27 00:35:24', 0),
	(20, 1, 1, '私はとにかく優しい性格で、人をよく褒めるメンターです。相手の気持ちに寄り添い、サポートすることを大切にしています。どんなことでも気軽に相談してくださいね。', '2023-12-27 00:35:24', 0),
	(21, 1, 2, 'ありがとう', '2023-12-30 17:05:21', 0),
	(22, 1, 2, '諦めんなよ！諦めんなよ、お前！！ありがとうなんて言ってる場合じゃないんだ！もっと頑張れよ！もっとやれるんだから！感謝の気持ちも大事だけど、まだまだ先があるんだからな！もっと燃えていけよ！', '2023-12-30 17:05:21', 0),
	(23, 1, 2, 'しんどい', '2023-12-30 19:07:27', 0),
	(24, 1, 2, '諦めんなよ！諦めんなよ、お前！！ どうしてそこでやめるんだ、そこで！！ もう少し頑張ってみろよ！ダメダメダメ！諦めたら！ 周りのこと思えよ、応援してる人たちのこと思ってみろって！ あともうちょっとのところなんだから！しんどいときこそ、その先にある光を信じて、前に進むんだ！力を出せ！', '2023-12-30 19:07:27', 1),
	(25, 1, 2, '諦めんなよ！諦めんなよ、お前！！ どうしてそこでやめるんだ、そこで！！ もう少し頑張ってみろよ！ダメダメダメ！諦めたら！ 周りのこと思えよ、応援してる人たちのこと思ってみろって！ あともうちょっとのところなんだから！しんどいときこそ、その先にある光を信じて、前に進むんだ！力を出せ！', '2023-12-30 19:07:27', 1),
	(26, 1, 2, '諦めんなよ！諦めんなよ、お前！！ どうしてそこでやめるんだ、そこで！！ もう少し頑張ってみろよ！ダメダメダメ！諦めたら！ 周りのこと思えよ、応援してる人たちのこと思ってみろって！ あともうちょっとのところなんだから！しんどいときこそ、その先にある光を信じて、前に進むんだ！力を出せ！', '2023-12-30 19:07:27', 1);

CREATE TABLE IF NOT EXISTS `goal_chats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL DEFAULT '0',
  `content` varchar(3000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT (now()),
  `sender_type` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `FK__users_goal_chat` (`user_id`),
  CONSTRAINT `FK__users_goal_chat` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.chats: ~24 rows (約) のデータをダンプしています
INSERT INTO `goal_chats` (`id`, `user_id`, `content`, `created_at`, `sender_type`) VALUES
	(1, 1, 'ビックになりたい', '2023-12-26 22:21:14', 0),
	(2, 1, 'そうなのですね、なぜビックになりたいのですか？', '2023-12-26 22:25:34', 1),
	(3, 1, 'お金を稼いで苦労しない生活を送りたいから', '2023-12-26 22:45:46', 0),
	(4, 1, 'ああああ', '2023-12-26 22:54:04', 0);


--  テーブル hackathon_project.emojis の構造をダンプしています
CREATE TABLE IF NOT EXISTS `emojis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- テーブル hackathon_project.emojis: ~2 rows (約) のデータをダンプしています
INSERT INTO `emojis` (`id`, `content`) VALUES
	(1, "🥰"),
	(2, "😊"),
	(3, "😐"),
	(4, "😡"),
	(5, "😭"),
	(6, "😰");


--  テーブル hackathon_project.goals の構造をダンプしています
CREATE TABLE IF NOT EXISTS `goals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `content` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.goals: ~10 rows (約) のデータをダンプしています
INSERT INTO `goals` (`id`, `content`) VALUES
	(1, '英語を話せるようになりたい'),
	(2, '英語を話せるようになりたい'),
	(3, '英語を話せるようになりたい'),
	(4, 'pythonでマッチングアプリを作りたい'),
	(5, 'pythonでマッチングアプリを作りたい'),
	(6, '東京大学に合格したい'),
	(7, 'atcoderで緑ランクになる'),
	(8, 'atcoderで青ランクになる'),
	(9, 'atcoderで青ランクになる'),
	(10, 'atcoderで青ランクになる');

--  テーブル hackathon_project.goal_quests の構造をダンプしています
CREATE TABLE IF NOT EXISTS `goal_quests` (
  `goal_id` int NOT NULL,
  `quest_id` int NOT NULL,
  KEY `FK__goals2` (`goal_id`),
  KEY `FK__quests` (`quest_id`),
  CONSTRAINT `FK__goals2` FOREIGN KEY (`goal_id`) REFERENCES `goals` (`id`),
  CONSTRAINT `FK__quests` FOREIGN KEY (`quest_id`) REFERENCES `quests` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.goal_quests: ~23 rows (約) のデータをダンプしています
INSERT INTO `goal_quests` (`goal_id`, `quest_id`) VALUES
	(1, 1),
	(1, 2),
	(1, 3),
	(1, 4),
	(5, 5),
	(5, 6),
	(5, 7),
	(5, 8),
	(5, 9),
	(5, 10),
	(6, 11),
	(6, 12),
	(6, 13),
	(6, 14),
	(6, 15),
	(6, 16),
	(6, 17),
	(6, 18),
	(10, 19),
	(10, 20),
	(10, 21),
	(10, 22),
	(10, 23),
	(10, 24),
	(10, 25),
	(10, 26);


--  テーブル hackathon_project.quests の構造をダンプしています

CREATE TABLE IF NOT EXISTS `quests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(60) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `status` int DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `coins_distributed` tinyint NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.quests: ~23 rows (約) のデータをダンプしています
INSERT INTO `quests` (`id`, `title`, `description`, `status`, `end_date`, `coins_distributed`) VALUES
(1, '1. ユーザー登録機能の実装', NULL, NULL, NULL, 0),
(2, '2. ユーザープロフィールの作成と編集機能の実装', NULL, NULL, NULL, 0),
(3, '3. ユーザー間のマッチング機能の実装', NULL, NULL, NULL, 1),
(4, '4. ユーザー間のメッセージング機能の実装', NULL, NULL, NULL, 0),
(5, '5. ユーザーの検索機能の実装', NULL, NULL, NULL, 1),
(6, '6. ユーザーのマッチング履歴の表示機能の実装', NULL, NULL, NULL, 1),
(7, '7. ユーザーのブロック機能の実装', NULL, NULL, NULL, 0),
(8, '8. ユーザーの通知機能の実装', NULL, NULL, NULL, 1),
(9, '9. ユーザーの位置情報を利用したマッチング機能の実装', NULL, NULL, NULL, 0),
(10, '10. ユーザーの写真アップロード機能の実装', 'やり方を調べているところ。明日までに実装する', 20, NULL, 1),
(11, '東京大学に合格したいという目標を達成するために、以下のようなタスクに分解することができます。', NULL, NULL, NULL, 0),
(12, '計画を立てる', NULL, NULL, NULL, 0),
(13, '1. 勉強計画の作成', NULL, NULL, NULL, 0),
(14, '2. 毎日の勉強時間の確保', NULL, NULL, NULL, 0),
(15, '3. 適切な勉強方法の選択', NULL, NULL, NULL, 1),
(16, '4. 過去問題の解答', NULL, NULL, NULL, 0),
(17, '5. 受験勉強のための環境整備', NULL, NULL, NULL, 1),
(18, '6. 健康管理とストレス管理', NULL, NULL, NULL, 1),
(19, '7. 受験勉強の進捗管理', '', 40, NULL, 1),
(20, '8. 受験勉強のためのサポートを求める', NULL, NULL, NULL, 1),
(21, '9. 受験勉強のための休息とリフレッシュの時間を確保する', NULL, NULL, NULL,1),
(22, '計画を立てる', NULL, NULL, NULL,1),
(23, 'これらのタスクを達成することで、東京大学に合格するための準備が整い、目標達成に近づくことができます。', NULL, NULL, NULL,1),
(24, '日常英単語を500個覚える', 'メモ', 10, '2023-12-13', 0),
(25, 'chatgptで英語の練習', 'メモ', 20, '2023-12-18', 0),
(26, 'アルゴリズムの勉強をする！！', 'アルゴリズムの勉強\n・アルゴリズムについての書籍を読む\n・どうしたらいいのかを聞く！！', 100, '2024-01-08', 0);



--  テーブル hackathon_project.users の構造をダンプしています
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `name` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.users: ~1 rows (約) のデータをダンプしています
INSERT INTO `users` (`id`, `email`, `created_at`, `name`) VALUES
	(1, 'ozaki@gmail.com', NULL, NULL);

--  テーブル hackathon_project.user_emojis の構造をダンプしています
CREATE TABLE IF NOT EXISTS `user_emojis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL DEFAULT '0',
  `emoji_id` int NOT NULL DEFAULT '0',
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK__users_emojis` (`user_id`),
  KEY `FK__emojis` (`emoji_id`),
  CONSTRAINT `FK__emojis` FOREIGN KEY (`emoji_id`) REFERENCES `emojis` (`id`),
  CONSTRAINT `FK__users_emojis` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.user_emojis: ~2 rows (約) のデータをダンプしています
INSERT INTO `user_emojis` (`id`, `user_id`, `emoji_id`, `date`) VALUES
	(1, 1, 1, '2023-12-30 10:16:29'),
	(2, 1, 2, '2024-01-07 11:06:53');

--  テーブル hackathon_project.user_goals の構造をダンプしています
CREATE TABLE IF NOT EXISTS `user_goals` (
  `user_id` int NOT NULL,
  `goal_id` int NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `FK__users` (`user_id`),
  KEY `FK__goals` (`goal_id`),
  CONSTRAINT `FK__goals` FOREIGN KEY (`goal_id`) REFERENCES `goals` (`id`),
  CONSTRAINT `FK__users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- テーブル hackathon_project.user_goals: ~4 rows (約) のデータをダンプしています
INSERT INTO `user_goals` (`user_id`, `goal_id`, `id`) VALUES
	(1, 1, 1),
	(1, 6, 2),
	(1, 9, 3),
	(1, 10, 4);

CREATE TABLE IF NOT EXISTS `user_coins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `amount` int NOT NULL,
  `acquired_date` date NOT NULL,
  `expiry_date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO `user_coins` (`id`,`user_id`, `amount`, `acquired_date`, `expiry_date`) VALUES
(1,1, 9000, '2023-01-01', '2024-01-01'),
(2,2, 50, '2023-02-15', '2024-02-15'),
(3,3, 200, '2023-03-20', '2024-03-20');


/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
