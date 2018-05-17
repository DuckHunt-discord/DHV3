<?php


require_once 'vendor/autoload.php';
$servername = "localhost";
$username   = "duckhunt_web";
$password   = "duckhunt_web";

$admins     = array(
    138751484517941259 // EyesOfCreeper#0001
);
$moderators = array(
    380118196742651906, // @rulebritannia 🇬🇧#6894
    151016183401938944, // @Crumble_#8877
    183273311503908864, // @Olpouin#6797
    85708771053043712,  // @otagueule#7958
    251996890369884161, // @Subtleknifewielder#1927
    181846573351829504, // @PierrePV#3537
    296573428293697536, // @⚜HappyWizzz⚜#5928
);

$translators   = array(
    193431551034392576, // barnabinnyu#193431551034392576
    211888559735570433, // pun1sher#211888559735570433
    316724329570238465, // !   a#316724329570238465
    350397621027864576, // Lord DréByte#350397621027864576
    202979770235879427, // estudiante🌎#202979770235879427
    214345196207341572, // Hannes#214345196207341572
    225383218113675264, // Cristian1914#225383218113675264
    236187090881085440, // Areisp#236187090881085440
    286806848693338112, // Aragogne#286806848693338112
    151016183401938944, // Crumble_#151016183401938944
    335578928335028236, // kei#335578928335028236
    349659491219931136, // Skrayern#349659491219931136
    263216424737046528, // SlimyMelon#263216424737046528
    278599626922131459, // Legolas#278599626922131459
    255009837002260482, // Koen02#255009837002260482
    135446225565515776, // Taoshi#135446225565515776
    297391115890589699, // ﾠﾠﾠﾠﾠ#297391115890589699
    331319593681289216, // ImparuZ#331319593681289216

);
$bug_hunters   = array(
    251996890369884161, // Subtleknifewielder#251996890369884161
);
$proficients   = array(
    174670292994621440, // sholan#174670292994621440
    329940268457525249, // Deathclaw#329940268457525249
    251996890369884161, // Subtleknifewielder#251996890369884161
    380118196742651906, // rulebritannia 🇬🇧#380118196742651906
    231117724317646849, // Heroesflorian#231117724317646849
    135446225565515776, // Taoshi#135446225565515776
    191602541534904321, // Volcanard#191602541534904321
);
$retired_staff = array(
    94822638991454208,  // Diagamma#7456

);
$partners      = array(
    120193744707256320, // Dr Zachary Smith#120193744707256320
);
$donators      = array(
    296573428293697536, // ⚜HappyWizzz⚜#296573428293697536
    304581891590324225, // Will#304581891590324225
);


try {
    $conn = new PDO("mysql:host=$servername;dbname=DHV3", $username, $password);
    // set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    //echo "Connected successfully";
}
catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
    die;
}


if (isset($_GET['cid'])) {
    $loader = new Twig_Loader_Filesystem('templates');

    $twig = new Twig_Environment($loader, array(//'cache' => 'cache',
    ));
    $twig->addExtension(new \Snilius\Twig\SortByFieldExtension());

    $channel_id   = (int)$_GET['cid'];
    $db_cid_query = $conn->prepare("SELECT id, channel_name FROM channels WHERE channel=:channel_id");
    $db_cid_query->bindParam(':channel_id', $channel_id);
    $db_cid_query->execute();
    $db_c            = $db_cid_query->fetch();
    $db_channel_id   = $db_c['id'];
    $db_channel_name = $db_c['channel_name'];

    if (isset($_GET['pid'])) { // On a la channel et le player

        $player_id          = (int)$_GET['pid'];
        $player_stats_query = $conn->prepare("SELECT * FROM players WHERE channel_id=:channel_id and id_=:player_id LIMIT 1");
        $player_stats_query->bindParam(':channel_id', $db_channel_id);
        $player_stats_query->bindParam(':player_id', $player_id);
        $player_stats_query->execute();

        if ($player_stats_query->rowCount() == 0) {
            http_response_code(404);
            die("Player or channel not found!");
        }

        $player_stats = $player_stats_query->fetch();


        //print_r($player_stats);

        $player_stats['channel_name'] = $db_channel_name;
        $player_stats['channel_id']   = $channel_id;

        $player_stats['badges'] = array(
            "banned"        => $player_stats['banned'],
            "no_weapon"     => (time() - $player_stats['confiscated']) < 0,
            "admin"         => in_array($player_stats['id_'], $admins),
            "moderator"     => in_array($player_stats['id_'], $moderators),
            "translator"    => in_array($player_stats['id_'], $translators),
            "bug_hunter"    => in_array($player_stats['id_'], $bug_hunters),
            "proficient"    => in_array($player_stats['id_'], $proficients),
            "retired_staff" => in_array($player_stats['id_'], $retired_staff),
            "partner"       => in_array($player_stats['id_'], $partners),
            "donator"       => in_array($player_stats['id_'], $donators),
        );

        $player_stats['achievements'] = array(
            "time_played_1"  => $player_stats['givebacks'] > 7,
            "time_played_2"  => $player_stats['givebacks'] > 30,
            "clueless"       => $player_stats['exp'] < -15,
            "scientist"      => $player_stats['exp'] > 2090,
            "max_level"      => $player_stats['exp'] > 11111,
            "cheater"        => $player_stats['exp'] > 1000000,
            "baby_lover"     => $player_stats['killed_baby_ducks'] < 5,
            "murderer"       => $player_stats['murders'] > 0,
            "first_blood"    => $player_stats['killed_ducks'] > 1,
            "ducks_killed_1" => $player_stats['killed_ducks'] > 10,
            "ducks_killed_2" => $player_stats['killed_ducks'] > 100,
            "ducks_killed_3" => $player_stats['killed_ducks'] > 500,
            "ducks_killed_4" => $player_stats['killed_ducks'] > 1000,
            "ducks_killed_5" => $player_stats['killed_ducks'] > 2000,
            "ducks_killed_6" => $player_stats['killed_ducks'] > 4000,
            "lucky_user"     => $player_stats['exp_won_with_clover'] > 500,

        );


        echo $twig->render('duckstats_player.twig', $player_stats);


    } else {
        // Player not passed, displaying chan statistics
        $players_array_query = $conn->prepare("SELECT * FROM players WHERE channel_id=:channel_id AND (exp <> 0 OR killed_ducks > 0) ORDER BY exp DESC");
        $players_array_query->bindParam(':channel_id', $db_channel_id);
        $players_array_query->execute();

        if ($players_array_query->rowCount() == 0) {
            http_response_code(404);
            die("Channel not found!");
        }

        $players_array = $players_array_query->fetchall();


        $total_normal_ducks     = 0;
        $total_super_ducks      = 0;
        $total_baby_ducks       = 0;
        $total_moad_ducks       = 0;
        $total_mechanical_ducks = 0;
        $total_players_killed   = 0;


        foreach ($players_array as &$player) {
            $total_normal_ducks     += $player['killed_normal_ducks'];
            $total_super_ducks      += $player['killed_super_ducks'];
            $total_baby_ducks       += $player['killed_baby_ducks'];
            $total_moad_ducks       += $player['killed_mother_of_all_ducks'];
            $total_mechanical_ducks += $player['killed_mechanical_ducks'];
            $total_players_killed   += $player['killed_players'];
        }


        $passed = [
            "players"                => $players_array,
            "channel_name"           => $db_channel_name,
            "channel_id"             => $channel_id,
            "total_normal_ducks"     => $total_normal_ducks,
            "total_super_ducks"      => $total_super_ducks,
            "total_baby_ducks"       => $total_baby_ducks,
            "total_moad_ducks"       => $total_moad_ducks,
            "total_mechanical_ducks" => $total_mechanical_ducks,
            "total_players_killed"   => $total_players_killed,
        ];


        echo $twig->render('duckstats_channel.twig', $passed);


    }


} else // Il manque des paramètres, RIP

{

    header("Location: .", true, 301);
    die();

}
